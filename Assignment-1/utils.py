class BasicLFSR:
    def __init__(self, seed):
        self.state = seed

    def step(self):
        # XOR bit 0 and 1
        feedback = self.state[0] ^ self.state[1]
        self.state = self.state[1:] + [feedback]
        return self.state[-1]

    def run(self, steps):
        output = []
        for _ in range(steps):
            bit = self.step()
            output.append(bit)
        return output

class GeneralLFSR:
    def __init__(self, seed, tap_positions):
        self.state = seed[:]
        self.tap_positions = tap_positions  

    def step(self):
        # XOR feedback by tap
        feedback = 0
        for pos in self.tap_positions:
            feedback ^= self.state[pos]
        self.state = self.state[1:] + [feedback]
        return self.state[-1]

    def run(self, steps):
        output = []
        for _ in range(steps):
            bit = self.step()
            output.append(bit)
        return output