from openai import OpenAI
import csv
import requests

import julia
julia_rt='/home/graham/dist/julia-cedar/vanilla/latest/bin/julia'
julia.install(julia=julia_rt)
julia.Julia(runtime=julia_rt)
from julia import Pkg 
Pkg.add("CedarSim")
Pkg.add("SpectreNetlistParser")

from julia import CedarSim
from julia import SpectreNetlistParser

from pinecone import Pinecone
from pinecone import ServerlessSpec
import time

oai_key = ""
pc_key = ""

class oai_gpt:
  headers = {}
  model_name = ""
  cost = 0
  prompt_tokens = 0
  comp_tokens = 0

  def __init__(self, oai_key, model_name="gpt-4o-mini"):
    self.headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {oai_key}"
    }
    self.model_name = model_name
    
  def prompt(self, question):
    prompt_content = [{"type": "text", "text": question}]
    payload = {
      "model": self.model_name,
      "messages": [
        {
          "role": "user",
          "content": prompt_content
        }
      ],
      "max_tokens": 1024
    }

    run = True
    while(run):
      try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=self.headers, json=payload).json()
        run = False
      except:
        print("oai query failure")
        time.sleep(30)
        run = True
    
    if 'usage' in response:
      self.prompt_tokens += response['usage']['prompt_tokens']
      self.comp_tokens += response['usage']['completion_tokens']
      self.cost += 0.15 * (self.prompt_tokens / 1000000)
      self.cost += 0.60 * (self.comp_tokens / 1000000)
   
    if 'choices' not in response:
      for k in response:
        print(k, response[k])

    return response['choices'][0]['message']['content']

  def print_cost(self):
    print(f"gpt-4o-mini cost: $0.15/1M input tokens x {self.prompt_tokens} + $0.60/1M output tokens x {self.comp_tokens} = ${self.cost:.6f}")


class rag_controller(oai_gpt):
  pc = {}
  index = {}
  pc_model_name = ""
  pc_index_name = ""

  def __init__(self, name, oai_key, pc_key, oai_model_name="gpt-4o-mini", pc_model_name="multilingual-e5-large"):
    super().__init__(oai_key, oai_model_name)
    self.pc = Pinecone(api_key=pc_key)
    self.pc_model_name = pc_model_name
    self.pc_index_name = name

  def init_new_index(self, dim):
    if self.pc.has_index(self.pc_index_name):
      self.pc.delete_index(self.pc_index_name)
    self.pc.create_index(
      name=self.pc_index_name,
      dimension=dim,
      metric="cosine",
      spec=ServerlessSpec(
          cloud='aws',
          region='us-east-1'
      )
    )
    while not self.pc.describe_index(self.pc_index_name).status['ready']:
      time.sleep(1)

  def build_rag(self, ds, embed_bs, upsert_bs):
    question_embedding = []
    vectors = []
    
    for i in range(0, len(ds), embed_bs):
      question_embedding_batch = self.pc.inference.embed(
        model=self.pc_model_name,
        inputs=[d['question'] for d in ds[i : i+embed_bs]],
        parameters={"input_type": "query"}
      )
      question_embedding.extend(question_embedding_batch)

    for d, e in zip(ds, question_embedding):
      vectors.append({
        "id": d['id'],
        "values": e['values'],
        "metadata": {"question": d['question'], "answer": d['answer']}
      })

    self.index = self.pc.Index(self.pc_index_name)
    for i in range(0, len(vectors), upsert_bs):
      run = True
      while(run):
        try:
          self.index.upsert(
            vectors=vectors[i:i + upsert_bs],
            namespace="example-namespace"
          )
          run = False
        except:
          print("upsert failure")
          time.sleep(30)
          run = True
    while not self.pc.describe_index(self.pc_index_name).status['ready']:
      time.sleep(1)

  def retrieve(self, question, top_k=3):
    results = None
    while(results == None or len(results['matches']) < top_k):
      embedding = self.pc.inference.embed(
        model=self.pc_model_name,
        inputs=[question],
        parameters={
          "input_type": "query"
        }
      )

      results = self.index.query(
          namespace="example-namespace",
          vector=embedding[0].values,
          top_k=3,
          include_values=False,
          include_metadata=True
      )
      if(len(results['matches']) < top_k):
         time.sleep(3)
    return results['matches']

  def print_index_states(self):
    print(self.pc.describe_index_stats())

  def check_spectre(self, data):
    try:
      parsed_data = SpectreNetlistParser.parse(data)
      print(dir(parsed_data))
      print(parsed_data.jl_value)
      print(parsed_data)
    except Exception as e:
      return str(e)
    return ""
  
  def process_answer(self, data):
    if data.count("```") == 2:
      start_idx = data.find("```") + 3
      end_idx = data.rfind("```")
      return data[start_idx:end_idx]
    return ""
  
  def build_rag_prompt(self, question, k=3):
    rag_data = self.retrieve(question, k)
    rag_question = "You are a cadence simulation expert. You are tasked with making simple stimulus files for any type of analog or digital circuit. \n"
    rag_question += "These stimulus files should not instantiate any active or passive components, specifically only nets for their inputs.\n"
    rag_question += "You should also not incude any text outside of your response other than the comments or code surrounded by ```\n"
    rag_question += "Here are " +str(k)+" similar stimulus files for you to guide your response.\n\n"
    rag_question += "Context:\n"
    for idx in range(k):
        rag_question += f"Q{idx + 1}: {rag_data[idx]['metadata']['question']}\n"
        rag_question += f"A{idx + 1}: {rag_data[idx]['metadata']['answer']}\n\n"
    rag_question += "Using the above context, please provide a helpful answer to the following question:\n"
    rag_question += f"{question}\n"
    return rag_question

  def prompt(self, question, tries):
    passed = False
    n = 0
    rag_question = self.build_rag_prompt(question)
    answer = super().prompt(rag_question)
    answer = self.process_answer(answer)
    e = self.check_spectre(answer)
    new_question = rag_question
    while(e != ""):
      new_question += "Your answer:\n"
      new_question += answer + "\n\n"
      new_question += "Unfortunately, your previous code did not pass code inspection, the parser returned the following issues or exceptions:\n"
      new_question += e+"\n\n"
      new_question += "Please answer again using the previous information\n"

      answer = super().prompt(new_question)
      answer = self.process_answer(answer)
      print(new_question)
      print(answer)
      n += 1
      e = self.check_spectre(answer)
      if(n == tries):
        break
    if(e == ""):
      passed = True
    return passed, answer

  def direct_prompt(self, question):
    passed = False
    direct_question = "You should not incude any text outside of your response other than the code surrounded by ```\n"
    direct_question += question
    answer = super().prompt(direct_question)
    answer = self.process_answer(answer)
    e = self.check_spectre(answer)
    if(e == ""):
      passed = True
    return passed, answer

class line_item:
  prompt = ""
  human_answer = ""
  circuit_type = ""
  specificity = ""
  complexity = ""
  verified = ""
  gpt_answer = ""
  backup = ""
  def __init__(self, prompt, human_answer, circuit_type, specificity, complexity, verified, rag_answer, rag_pass, gpt_answer, gpt_pass, backup):
    self.prompt = prompt
    self.human_answer = human_answer
    self.circuit_type = circuit_type
    self.specificity = specificity
    self.complexity = complexity
    self.verified = verified
    self.rag_answer = rag_answer
    self.rag_pass = rag_pass
    self.gpt_answer = gpt_answer
    self.gpt_pass = gpt_pass
    self.backup = backup
  # poor man pickling
  def to_list(self):
    return [self.prompt, self.human_answer, self.circuit_type, self.specificity, self.complexity, self.verified, self.rag_answer, self.rag_pass, self.gpt_answer, self.gpt_pass , self.backup]

class file_master:
  header = {}
  cs = []
  in_fname = ""
  out_fname = ""

  def __init__(self, in_fname, out_fname):
    self.in_fname = in_fname
    self.out_fname = out_fname

  def build_ds(self):
    ds = []
    ts = []
    # this would be a lot better with some python itterable trickery but idfc
    with open(self.in_fname, 'r', newline='') as f:
      reader = csv.reader(f, delimiter=',', quotechar='"')
      i=0
      for line in reader:
        if line[0] == 'prompt' or line[0] == '':
          self.header = line_item(line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7], line[8], line[9], line[10])
          continue
        else:
          self.cs.append(line_item(line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7], line[8], line[9], line[10]))
          if line[1] == '':
            ts.append({'id': str(i), 'question': line[0], 'answer': ''})
          else:
            ds.append({'id': str(i), 'question': line[0], 'answer': line[1]})
          i+=1
    return ds, ts

  def set_rag_answer(self, idx, answer, success):
      self.cs[idx].rag_answer = answer
      self.cs[idx].rag_pass = success
  
  def set_gpt_answer(self, idx, answer, success):
      self.cs[idx].gpt_answer = answer
      self.cs[idx].gpt_pass = success

  def save_ds(self):
    ds = []
    ts = []
    with open(self.out_fname, 'w', newline='') as f:
      writer = csv.writer(f, delimiter=',', quotechar='"')
      writer.writerow(self.header.to_list())
      for item in self.cs:
        writer.writerow(item.to_list())

f2 = """//Voltage Divider Testbench 
simulator lang=spectre //Spectre initialization  
//Parameters 
parameters R1 = 1k //Set parameter R1 to 1k ohms 
parameters R2 = 2k //Set parameter R2 to 2k ohms 
parameters Vparam = 5 //Set parameter Vparam for input voltage to 5V 
//Input Sources 
V0 (vin 0) vsource dc=Vparam //A DC voltage source named V0 between node 'vin' and global gnd node '0' with a voltage of Vparam 
//Voltage Divider Configuration 
R1 (vout vin) resistor r=R1 //Resistor R1 connected between node 'vin' and node 'vout' with resistance R1 
R2 (vout 0) resistor r=R2 //Resistor R2 connected between node 'vout' and global gnd node '0' with resistance R2"""

if __name__ == "__main__":
  in_fname = "201A_Dataset_12_15_24.csv"
  out_fname = "201A_Dataset_12_15_24_out.csv"
  netlist_file = "spectre/293_input.scs"
  # tries until giving up on correct syntax
  tries = 10
  

  fm = file_master(in_fname, out_fname)
  ds, ts = fm.build_ds()
  i = 0
  answers = []
  for item in ds:
    name = "bgillm1"
    rag = rag_controller(name, oai_key, pc_key)
    rag.init_new_index(1024)
    new_ds = ds.copy()
    new_ds.pop(i)
    rag.build_rag(new_ds, 96, 50)
    success, answer = rag.prompt(item['question'], tries)
    fm.set_rag_answer(int(item['id']), answer, success)
    print(int(item['id']))
    print(item['question'])
    print("RAG: \n" + answer)
    success, answer = rag.direct_prompt(item['question'])
    fm.set_gpt_answer(int(item['id']), answer, success)
    print("GPT: \n" + answer)

    i+=1
  fm.save_ds()
