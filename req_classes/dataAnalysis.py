


"""  ### FOr each picture
Penalization = n(dead seeds) * (50/n(total))
Where:
n = total seeds
n(mortas) = dead seeds (seeds that didn't germinated)


= 2 * 50 /20 

"""
# summary.csv

# fileName  penalization value
# N1A.jpg   0.3
# N2A.jpg   0.4


"""
ti = length of the analyzed seedling
T =  average length of the entire batch(image)
n = plants in the batch (image)

seedVigorIndex = max (0,  (1 - (summation_i_1_to_n( abs(Ti - T) / n * T) * 1000 )   -   Penalization   ))

"""
from .contour_processor import Seed
from proj_settings import MainSettings, SeedHealth
import json
import numpy as np
import traceback

settings_path = MainSettings.settings_json_file_path

# with open(settings_path, 'r') as f:
#     dict_settings = json.load(f)



class BatchAnalysisNew:
    def __init__(self, img_path, batchNumber, seedObjList:list[Seed]):
        self.batchNumber = batchNumber
        self.dict_settings = None
        self.seedObjList = seedObjList


        self.list_total_seed_lengths = []

        self.n_total_seeds_in_image = 0

        self.germinated_seed_count = 0
        self.dead_seed_count = 0
        self.abnormal_seed_count = 0

        self.growth = 0
        self.penalization = 0
        self.uniformity = 0
        self.seed_vigor_index = 0

        self.avg_total_length_settings = 0  # in pixels
        self.avg_total_length_calculated = 0
        self.avg_hypocotyl_length = 0  # in cm
        self.avg_root_length = 0 # in cm
        self.std_deviation = 0
        self.germination_percent = 0

        

        self.recalculate_all_metrics()


    def recalculate_all_metrics(self):

        settings_path = MainSettings.settings_json_file_path

        with open(settings_path, 'r') as f:
            self.dict_settings = json.load(f)


                

        self.get_seed_class_count()

        self.calculate_averages()
        self.calculate_growth_or_Crescimento()
        self.calc_penalization()
        self.calculate_uniformity_or_Uniformidade()
        self.calculate_seed_vigor_index()
        self.calculate_std_deviation_and_other()

    def get_seed_class_count(self):
        self.dead_seed_count, self.abnormal_seed_count, self.germinated_seed_count = 0,0,0

        for seedObj in self.seedObjList:
            if seedObj.seed_health == SeedHealth.DEAD_SEED:
                self.dead_seed_count+=1
            elif seedObj.seed_health == SeedHealth.ABNORMAL_SEED:
                self.abnormal_seed_count+=1
            elif seedObj.seed_health == SeedHealth.NORMAL_SEED:
                self.germinated_seed_count+=1

        print("Dead seed count", self.dead_seed_count)
        print("Abnormal seed count", self.abnormal_seed_count)
        print("Normal seed count", self.germinated_seed_count)

        self.n_total_seeds_in_image = self.dead_seed_count + self.abnormal_seed_count+self.germinated_seed_count


    def calc_penalization(self):
        self.penalization = self.dead_seed_count * 50 / self.n_total_seeds_in_image
        return self.penalization


    def calculate_averages(self):
        
        self.list_total_seed_lengths = []
        self.list_hypocotyl_seed_lengths = []
        self.list_root_lengths = []


        for seedObj in self.seedObjList:
            
            self.list_total_seed_lengths.append(seedObj.total_length_cm)
            self.list_hypocotyl_seed_lengths.append(seedObj.hyperCotyl_length_cm)
            self.list_root_lengths.append(seedObj.radicle_length_cm)

        
        self.avg_total_length_calculated = round(sum(self.list_total_seed_lengths) /  len(self.seedObjList), 2)
        self.avg_total_length_settings = self.dict_settings['average_seed_total_length']
        try:

            self.avg_hypocotyl_length = round(sum(self.list_hypocotyl_seed_lengths) /  len(self.seedObjList),2)
            self.avg_root_length = round(sum(self.list_root_lengths) /  len(self.seedObjList), 2)
        except Exception as e:
            print(traceback.format_exc())
            



    def calculate_uniformity_or_Uniformidade(self):
        # seedVigorIndex = max (0,  (1 - (summation_i_1_to_n( abs(Ti - T) / n * T) * 1000 )   -   Penalization   ))     

        # sortedList = sorted(self.list_total_seed_lengths)
        # centralIndex = (self.n_total_seeds_in_image - 1) // 2
    
        # if self.n_total_seeds_in_image %2 ==0:
        #     medianSeedLength = (sortedList[centralIndex] + sortedList[centralIndex+1] ) /2
        # else:
        #     medianSeedLength = sortedList[centralIndex]

               
        abs_sum = sum([abs(l_seed - self.avg_total_length_settings) for l_seed in self.list_total_seed_lengths])

        uni_ = (1 -  (abs_sum / (self.n_total_seeds_in_image * self.avg_total_length_settings))) * 1000 - self.penalization 

        self.uniformity = int(max(0, uni_))


    def calculate_growth_or_Crescimento(self):
        """ growth (or Crescimento) = avg of seed lengths(rad+hyp) / max length * 1000
        """
        ## wrong formula before       
        # self.growth = self.avg_total_length / max(self.list_total_seed_lengths) * 1000

        self.ph_ = self.dict_settings['ph']
        self.pr_ = self.dict_settings['pr']

        self.growth = min(self.avg_root_length* self.pr_ + self.avg_hypocotyl_length *self.ph_, 1000)


        
    def calculate_seed_vigor_index(self):
        """ Vigor = Pc * growth (or Crescimento) + Pu * Uniformity (or Uniformidade)"""
        self.Pc = self.dict_settings['weights_factor_growth_Pc']
        self.Pu = self.dict_settings['weights_factor_uniformity_Pu']
        self.seed_vigor_index = self.Pc * self.growth + self.Pu * self.uniformity

    def calculate_std_deviation_and_other(self):
        self.std_deviation = round(np.std(self.list_total_seed_lengths),2)
        self.germination_percent =  round(self.germinated_seed_count/ self.n_total_seeds_in_image * 100, 2)











class BatchAnalysis:
    def __init__(self, img_path, batchNumber, list_hypercotyl_radicle_lengths, dead_seed_max_length_r_h, 
                 abnormal_seed_max_length_r_h, normal_seed_max_length_r_h,
                 weights_factor_growth_Pc = 0.7, weights_factor_uniformity_Pu=0.3) -> None:
        self.batchNumber = batchNumber
        self.list_hypercotyl_radicle_lengths = list_hypercotyl_radicle_lengths
        self.dead_seed_max_length_r_h = dead_seed_max_length_r_h
        self.abnormal_seed_max_length_r_h = abnormal_seed_max_length_r_h
        self.normal_seed_max_length_r_h = normal_seed_max_length_r_h

        self.list_total_seed_lengths = []

        self.n_total_seeds_in_image = 0

        self.germinated_seed_count = 0
        self.dead_seed_count = 0
        self.abnormal_seed_count = 0

        self.growth = 0
        self.penalization = 0
        self.uniformity = 0
        self.seed_vigor_index = 0

        self.Pc = weights_factor_growth_Pc
        self.Pu = weights_factor_uniformity_Pu


        self.get_abnormal_normal_dead_seed_count()
        self.calculate_growth_or_Crescimento()
        self.calc_penalization()
        self.calculate_uniformity_or_Uniformidade()
        self.calculate_seed_vigor_index()

    def get_dead_seed_count(self):
        self.list_total_seed_lengths = [h+r for h,r in self.list_hypercotyl_radicle_lengths]
        self.n_total_seeds_in_image = len(self.list_hypercotyl_radicle_lengths)

        for total_length_seed in self.list_total_seed_lengths:
            
            if total_length_seed >= self.dead_seed_max_length_r_h:
                self.germinated_seed_count+=1
            else:
                self.dead_seed_count+=1

    def get_abnormal_normal_dead_seed_count(self):
        self.list_total_seed_lengths = [h+r for h,r in self.list_hypercotyl_radicle_lengths]
        self.n_total_seeds_in_image = len(self.list_hypercotyl_radicle_lengths)

        for total_length_seed in self.list_total_seed_lengths:
            
            if total_length_seed <= self.dead_seed_max_length_r_h:
                self.dead_seed_count+=1
            elif total_length_seed > self.dead_seed_max_length_r_h and total_length_seed <= self.normal_seed_max_length_r_h:
                self.abnormal_seed_count+=1
            else:
                self.germinated_seed_count+=1


    def calc_penalization(self):
        self.penalization = self.dead_seed_count * 50 / self.n_total_seeds_in_image
        return self.penalization


    def calculate_uniformity_or_Uniformidade(self):
        # seedVigorIndex = max (0,  (1 - (summation_i_1_to_n( abs(Ti - T) / n * T) * 1000 )   -   Penalization   ))     

        # sortedList = sorted(self.list_total_seed_lengths)
        # centralIndex = (self.n_total_seeds_in_image - 1) // 2
    
        # if self.n_total_seeds_in_image %2 ==0:
        #     medianSeedLength = (sortedList[centralIndex] + sortedList[centralIndex+1] ) /2
        # else:
        #     medianSeedLength = sortedList[centralIndex]
        
        avg_seed_length = sum(self.list_total_seed_lengths) / len(self.list_total_seed_lengths) 
        abs_sum = sum([abs(l_seed - avg_seed_length) for l_seed in self.list_total_seed_lengths])

        uni_ = (1 -  (abs_sum / (self.n_total_seeds_in_image * avg_seed_length))) * 1000 - self.penalization 

        self.uniformity = int(max(0, uni_))


    def calculate_growth_or_Crescimento(self):
        """ growth (or Crescimento) = avg of seed lengths(rad+hyp) / max length * 1000
        """
        avg_seed_length = sum(self.list_total_seed_lengths) / len(self.list_total_seed_lengths)
        self.growth = avg_seed_length / max(self.list_total_seed_lengths) * 1000

        
    def calculate_seed_vigor_index(self):
        """ Vigor = Pc * growth (or Crescimento) + Pu * Uniformity (or Uniformidade)"""

        self.seed_vigor_index = self.Pc * self.growth + self.Pu * self.uniformity
