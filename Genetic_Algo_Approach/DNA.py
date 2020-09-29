import numpy as np
from Eval_fitness import modAEP
from Utilities import GeneratePointsInCircle

class WindFarm_DNA:
  
  # Constructor (makes a random DNA), all dimension in meters
  def __init__(self, generate_genes: bool = True, num_of_turbines: int = 50, x_min: float = 50, x_max: float = 3950, y_min: float = 50, y_max:float = 3950, D_min: float = 400):
    self.genes = []
    self.fitness = 0.0;

    if(generate_genes == False):
      return

    max_candidates = num_of_turbines*20
    candidates_x = x_min + np.random.rand(max_candidates)*(x_max - x_min)
    candidates_y = y_min + np.random.rand(max_candidates)*(y_max - y_min)

    self.genes.append([candidates_x[0], candidates_y[0]])
    candidate_index = 1
    for i in range(1, num_of_turbines):
      found_flag = False
      while(not found_flag):
        dists = [((gene[0] - candidates_x[candidate_index])**2 + (gene[1] - candidates_y[candidate_index])**2) for gene in self.genes]
        if(min(dists) >= D_min**2):
          found_flag = True
          self.genes.append([candidates_x[candidate_index], candidates_y[candidate_index]])
        
        candidate_index += 1
        assert candidate_index < max_candidates, "All candidates tested !!!"


  # Printing the DNA in string format
  def __str__(self):
    break_after = 5  # number of lines before next newline
    for i in range(len(self.genes)):
      print(self.genes[i], end='\t')
      if((i+1)%break_after == 0):
        print()

    print("\nFitness Value: ", self.fitness)


  # Write to file
  def writeToFile(self, filename: str):
    f = open(filename, "w")
    f.write("x,y\n")
    for i in range(len(self.genes)):
      f.write(str(self.genes[i][0]) + "," + str(self.genes[i][1]) + "\n")
    f.close()

  
  # Fitness function (returns floating point % of "correct" characters)
  def calcFitness(self, powerCurve, wind_inst_freq):
     self.fitness = modAEP(np.array(self.genes), powerCurve, wind_inst_freq)
     
     if(self.fitness < 510):
      return self.fitness
     
     return 5**(self.fitness - 510)

  
  # Crossover
  def parthegenesis(self, p:float = 0.8, radius: float = 5, x_min:float = 50, x_max:float = 3950, y_min:float = 50, y_max:float = 3950, D_min: float = 400):
    # A new child
    child = WindFarm_DNA(generate_genes = False)

    # Allow single-parent to produce with probability p a 
    # child located in a random position within a circle of 
    # radius r centered at parent

    if np.random.rand() > p:
      child.genes = self.genes
      return child

    for parent_gene in self.genes:

      # generate 10 random genes in the circle around current parent
      num_points = 100
      candidate_genes = GeneratePointsInCircle(n = num_points, center_x = parent_gene[0], center_y = parent_gene[1], radius = radius)
      
      # choose the one that satisfies the constraints with previous ones, if none does return None
      found_flag = False
      for i in range(num_points):
        if(len(child.genes) == 0):
          child.genes.append(candidate_genes[i])
          found_flag = True
          break

        dists = [((gene[0] - candidate_genes[i][0])**2 + (gene[1] - candidate_genes[i][1])**2) for gene in child.genes]
        if(candidate_genes[i][0]>=x_min and candidate_genes[i][0]<=x_max and candidate_genes[i][1]>=y_min and candidate_genes[i][1]<=y_max and min(dists) >= D_min**2):
          found_flag = True
          child.genes.append(candidate_genes[i])
          break

      if found_flag == False:
        return None

    return child

  
  # Based on a mutation probability, shift turbine's x and y=coordinate with normal distribution 
  def mutate(self, mutationRate:float = 0.1, mu: float = 0, sigma: float = 1):
    for i in range(len(self.genes)):
      if (np.random.rand() < mutationRate):
        self.genes[i][0] += np.random.normal(mu, sigma)
        self.genes[i][1] += np.random.normal(mu, sigma)