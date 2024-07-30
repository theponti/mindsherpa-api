class GenerationStatistics:
    def __init__(
        self,
        input_time=0,
        output_time=0,
        input_tokens=0,
        output_tokens=0,
        total_time=0,
        model_name="llama3-8b-8192",
    ):
        self.input_time = input_time
        self.output_time = output_time
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.total_time = (
            total_time  # Sum of queue, prompt (input), and completion (output) times
        )
        self.model_name = model_name

    def get_input_speed(self):
        """
        Tokens per second calculation for input
        """
        if self.input_time != 0:
            return self.input_tokens / self.input_time
        else:
            return 0

    def get_output_speed(self):
        """
        Tokens per second calculation for output
        """
        if self.output_time != 0:
            return self.output_tokens / self.output_time
        else:
            return 0

    def add(self, other):
        """
        Add statistics from another GenerationStatistics object to this one.
        """
        if not isinstance(other, GenerationStatistics):
            raise TypeError("Can only add GenerationStatistics objects")

        self.input_time += other.input_time
        self.output_time += other.output_time
        self.input_tokens += other.input_tokens
        self.output_tokens += other.output_tokens
        self.total_time += other.total_time

    def get_stats(self):
        return {
            "model_name": self.model_name,
            "input": {
                "speed": self.get_input_speed(),
                "tokens": self.input_tokens,
                "time": self.input_time,
            },
            "output": {
                "speed": self.get_output_speed(),
                "tokens": self.output_tokens,
                "time": self.output_time,
            },
            "total": {
                "speed": (
                    (self.input_tokens + self.output_tokens) / self.total_time
                    if self.total_time != 0
                    else 0
                ),
                "tokens": self.input_tokens + self.output_tokens,
                "time": self.total_time,
            },
        }

    def __str__(self):
        return (
            f"\n## {self.get_output_speed():.2f} T/s ⚡\nRound trip time: {self.total_time:.2f}s  Model: {self.model_name}\n\n"
            f"| Metric          | Input          | Output          | Total          |\n"
            f"|-----------------|----------------|-----------------|----------------|\n"
            f"| Speed (T/s)     | {self.get_input_speed():.2f}            | {self.get_output_speed():.2f}            | {(self.input_tokens + self.output_tokens) / self.total_time if self.total_time != 0 else 0:.2f}            |\n"
            f"| Tokens          | {self.input_tokens}            | {self.output_tokens}            | {self.input_tokens + self.output_tokens}            |\n"
            f"| Inference Time (s) | {self.input_time:.2f}            | {self.output_time:.2f}            | {self.total_time:.2f}            |"
        )
