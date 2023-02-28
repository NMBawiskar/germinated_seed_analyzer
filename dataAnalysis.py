


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
T =  medium length of the entire batch(image)
n = plants in the batch (image)

seedVigorIndex = max (0,  (1 - (summation_i_1_to_n( abs(Ti - T) / n * T) * 1000 )   -   Penalization   ))

"""

class BatchAnalysis:
    def __init__(self, img_path, batchNumber, list_hypercotyl_radicle_lengths, dead_seed_max_length_r_h) -> None:
        self.batchNumber = batchNumber
        self.list_hypercotyl_radicle_lengths = list_hypercotyl_radicle_lengths
        self.dead_seed_max_length_r_h = dead_seed_max_length_r_h
        self.list_total_seed_lengths = []

        self.n_total_seeds_in_image = 0

        self.germinated_seed_count = 0
        self.dead_seed_count = 0
 
        self.penalization = 0
        self.seed_vigor_index = 0

        self.get_dead_seed_count()
        self.calc_penalization()
        self.calculate_seed_vigor_index()

    def get_dead_seed_count(self):
        self.list_total_seed_lengths = [h+r for h,r in self.list_hypercotyl_radicle_lengths]
        self.n_total_seeds_in_image = len(self.list_hypercotyl_radicle_lengths)

        for total_length_seed in self.list_total_seed_lengths:
            
            if total_length_seed >= self.dead_seed_max_length_r_h:
                self.germinated_seed_count+=1
            else:
                self.dead_seed_count+=1


    def calc_penalization(self):
        self.penalization = self.dead_seed_count * 50 / self.n_total_seeds_in_image
        return self.penalization


    def calculate_seed_vigor_index(self):
        # seedVigorIndex = max (0,  (1 - (summation_i_1_to_n( abs(Ti - T) / n * T) * 1000 )   -   Penalization   ))     

        sortedList = sorted(self.list_total_seed_lengths)
        centralIndex = (self.n_total_seeds_in_image - 1) // 2
    
        if self.n_total_seeds_in_image %2 ==0:
            medianSeedLength = (sortedList[centralIndex] + sortedList[centralIndex+1] ) /2
        else:
            medianSeedLength = sortedList[centralIndex]
        
        abs_sum = sum([abs(l_seed - medianSeedLength) for l_seed in self.list_total_seed_lengths])

        svi_ = (1 -  (abs_sum / (self.n_total_seeds_in_image * medianSeedLength))) * 1000 - self.penalization 

        self.seed_vigor_index = int(max(0, svi_))


