from utils import BasicLFSR, GeneralLFSR

if __name__ == "__main__":
    seed = [0, 1, 1, 0]  
    taps = [0, 1] 
    lfsr = BasicLFSR(seed)
    basic_stream = lfsr.run(20)

    general_lfsr = GeneralLFSR(seed, taps)
    general_stream = general_lfsr.run(20)

    print("Output stream:", basic_stream)
    print("General LFSR Output:", general_stream)