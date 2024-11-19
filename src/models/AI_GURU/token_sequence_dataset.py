import random
import os
import numpy as np
import torch
from torch.utils.data.dataset import Dataset


class TokenSequenceDataset(Dataset):

    def __init__(self, tokenizer, dataset_paths, block_size, simulate=False):

        pad_token_id = tokenizer.encode("[PAD]")[0]
        unk_token_id = tokenizer.encode("[UNK]")[0]

        # Read all lines from all files.
        lines = []
        for dataset_path in dataset_paths:
            assert os.path.isfile(dataset_path), f"Input file path {dataset_path} not found"
            lines += open(dataset_path, "r").readlines()

        # In simulation just use a few samples.
        if simulate:
            random.shuffle(lines)
            lines = lines[:10]

        # Turn lines into training examples. Also gather some statistics.
        self.examples = []
        unknown_tokens_set = []
        unknown_tokens = []
        tokens_count = 0
        unknown_token_lines_count = 0
        too_long_lines_count = 0
        encoded_lengths = []
        for line in lines:

            #Skip empty lines.
            line = line.strip()
            if line == "":
                continue

            # Encode the line.
            encoded_line = tokenizer.encode(line)
            encoded_lengths += [len(encoded_line)]
            tokens_count += len(encoded_line)

            # Create a warning about unknown tokens. And then skip the line.
            if unk_token_id in encoded_line:
                index = encoded_line.index(unk_token_id)
                token = tokenizer.decode(encoded_line[index])
                token = line.split()[index]
                if token not in unknown_tokens_set:
                    unknown_tokens_set += [token]
                #logger.warning(f"Skipping line because of unknown token {token}")
                unknown_tokens += [token]
                unknown_token_lines_count += 1
                continue

            # Skip sequence if it is too long.
            if len(encoded_line) > block_size:
                #logger.warning(f"Skipping line because it is too long... {len(encoded_line)} > {block_size}")
                too_long_lines_count += 1
                continue

            # Pad and truncate.
            tensor = np.full((block_size,), pad_token_id, dtype=np.longlong)
            tensor[:len(encoded_line)] = encoded_line
            assert len(tensor) == block_size

            self.examples += [{
                "input_ids": torch.tensor(tensor, dtype=torch.long),
                "labels": torch.tensor(tensor, dtype=torch.long)
            }]

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, i):
        return self.examples[i]
