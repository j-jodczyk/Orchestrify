from dataclasses import dataclass
import torch
import json

@dataclass
class SampleParam:
    """ Holds parameters used in generation """
    tracks_per_step: int
    bars_per_step: int
    model_dim: int
    percentage: int
    batch_size: 1
    temperature: float
    max_steps: int
    polyphony_hard_limit: float
    shuffle: bool
    verbose: bool
    ckpt: str

@dataclass
class Track:
    """ Holds track data """
    selected_bars: list
    autoregressive: bool
    ignore: bool

@dataclass
class Status:
    """ Holds status of model """
    tracks: list[Track]


@dataclass
class ModelMetadata:
    """ Holds model's metadata """
    model_dim: int

@dataclass
class ModelMeta:
    """ Holds loaded model and it's metadata """
    model: torch.ScriptModule
    meta: ModelMetadata

@dataclass
class Piece:
    resolution: int
    tracks: list

class TrackDensityEncoder:
    pass

@dataclass
class Step:
    start: int
    end: int
    step: list[list[bool]]
    context: list[list[bool]]

def status_to_selection_mask(status: Status):
    """
    Convert the status message into a track x bar matrix indicating selected bars.
    """
    ntracks = len(status.tracks)
    nbars = len(status.tracks[0].selected_bars)
    selection_mask = [[False] * nbars for _ in range(ntracks)]

    for track_num, track in enumerate(status.tracks):
        for bar_num, bar in enumerate(track.selected_bars):
            selection_mask[track_num][bar_num] = bool(bar)

    return selection_mask

def status_to_resample_mask(status: Status):
    """
    Get a boolean vector that indicates which tracks to resample.
    """
    resample_mask = [track.autoregressive for track in status.tracks]
    return resample_mask

def status_to_ignore_mask(status: Status):
    """
    Get a boolean vector that indicates which tracks to ignore.
    """
    ignore_mask = [track.ignore for track in status.tracks]
    return ignore_mask

def find_steps_inner(steps: list, selection_mask: list, resample_mask: list, ignore_mask: list, autoregressive, generated: list, param: SampleParam):
    tracks_per_step = max(1, min(param.tracks_per_step, len(selection_mask)))
    bars_per_step = max(1, min(param.bars_per_step, param.model_dim))

    sel = [row[:] for row in selection_mask]
    nt, nb = len(sel), len(sel[0])

    for i in range(nt):
        for j in range(nb):
            sel[i][j] = sel[i][j] and (resample_mask[i] if autoregressive else not resample_mask[i])

    covered = [[False] * nb for _ in range(nt)]
    num_context = (param.model_dim() - bars_per_step) // 2
    if autoregressive:
        num_context = param.model_dim() - bars_per_step

    ijs = [(i, j) for i in range(0, nt, tracks_per_step) for j in range(0, nb, bars_per_step)]

    for i, j in ijs:
        num_tracks = min(tracks_per_step, nt - i)
        kernel = [[False] * param.model_dim() for _ in range(num_tracks)]
        t = min(j, nb - param.model_dim())

        if autoregressive:
            right_offset = max((j + param.model_dim()) - nb, 0)
            t = min(j, nb - param.model_dim())
            for k in range((j > 0) * (num_context + right_offset), param.model_dim()):
                for n in range(num_tracks):
                    kernel[n][k] = True
        else:
            t = min(max(j - num_context, 0), nb - param.model_dim())
            for k in range(j - t, j - t + bars_per_step):
                for n in range(num_tracks):
                    kernel[n][k] = True

        step = [[sel[k][n] and kernel[k-i][n-t] for n in range(nb)] for k in range(nt)]
        if autoregressive:
            for k in range(nt):
                for n in range(t, t + param.model_dim()):
                    step[k][n] = step[k][n] and not generated[k][n]

        context = [[not ignore_mask[k] and not step[k][n] for n in range(nb)] for k in range(nt)]
        if autoregressive:
            for k in range(nt):
                if any(sel[k]):
                    for n in range(t, t + param.model_dim()):
                        context[k][n] = generated[k][n]

        if any(any(row) for row in step):
            steps.append(Step(t, t + param.model_dim(), step, context))

        for k in range(i, i + num_tracks):
            for n in range(t, t + param.model_dim()):
                generated[k][n] = generated[k][n] or step[k][n]
                covered[k][n] = covered[k][n] or kernel[k - i][n - t]

    if not all(all(row) for row in covered):
        raise RuntimeError("PIECE IS ONLY PARTIALLY COVERED")

def find_steps(selection_mask: list, resample_mask: list, ignore_mask: list, param: SampleParam):
    steps = []
    generated = [[False] * len(selection_mask[0]) for _ in range(len(selection_mask))]

    find_steps_inner(steps, selection_mask, resample_mask, ignore_mask, True, generated, param)
    find_steps_inner(steps, selection_mask, resample_mask, ignore_mask, False, generated, param)

    return steps

def status_subset(status: Status, start: int, step: int, tracks: list):
    pass

def status_rehighlight():
    pass

def piece_subset():
    pass

def piece_insert():
    pass

def update_status_instruments():
    pass

def override_piece_features():
    pass

@dataclass
class SampleControl:
    piece: Piece
    status: Status
    param: SampleParam
    meta: ModelMeta
    prompt: str

def make_state():
    pass

def sample_inner(sample_control: SampleControl, sequences: list[list[int]], model: torch.ScriptModule, inputs: list[torch.jit.IValue], param: SampleParam):
    logits = None
    past_key_values = None

    outputs = model.forward(inputs).to_tuple() # here's where model generates output
    logits = outputs[0][:, -1, :]
    past_key_values = outputs[1]

    # Apply masking to logits based on each sequence's mask
    for i, seq in enumerate(sequences):
        mask = sample_control[i].get_mask(seq)

        # Adjust logits for masked positions if masking is enabled and sequence is unfinished
        if not sample_control[i].finished and not param.internal_disable_masking:
            logits[i][torch.tensor(mask) == 0] = -float('inf')  # Mask to minimum probability

    # Apply temperature and sample the next tokens
    probs = torch.softmax(logits / param.temperature, dim=1)
    next_tokens = torch.multinomial(probs, 1)

    # Update inputs with the new tokens and past key values
    inputs.clear()
    inputs.append(next_tokens)

    # Add embeddings if encoder's configuration requires it
    if sample_control[0].enc.config.embed_dim:
        embed_dim = sample_control[0].enc.config.embed_dim
        c = torch.zeros((next_tokens.size(0), 1, embed_dim), dtype=torch.float32)
        for i in range(len(sequences)):
            embed = sample_control[i].get_bar_embed()
            c[i][0] = torch.tensor(embed[:embed_dim], dtype=torch.float32)
        inputs.append(c)

    # Add past key values to inputs
    inputs.append(past_key_values)

    # Append the sampled token to each sequence if the sequence is not finished
    for i in range(len(sequences)):
        if not sample_control[i].finished:
            sequences[i].append(next_tokens[i].item())

def generate(piece: Piece, status: Status, param: SampleParam, model: ModelMeta):
    """
    Generates a batch of MIDI pieces based on the given status, piece, and parameters.
    """
    param.temperature = max(param.temperature, 1e-6)
    terminated = False
    sample_control = [SampleControl(piece, status, param, model.meta) for _ in range(param.batch_size)]
    prompt = sample_control[0].prompt

    inputs = []
    x = torch.zeros((param.batch_size, len(prompt)), dtype=torch.int64)
    for k in range(param.batch_size):
        x[k] = torch.tensor(prompt, dtype=torch.int64)
        inputs.append(x)

    if sample_control[0].enc.config.embed_dim:
        embed_dim = sample_control[0].enc.config.embed_dim
        c = torch.zeros((param.batch_size, len(prompt), embed_dim), dtype=torch.float32)
        for k in range(param.batch_size):
            for i, token in enumerate(prompt):
                c[k][i] = torch.tensor(sample_control[0].embeds[i], dtype=torch.float32)
        inputs.append(c)

        state = make_state(param.batch_size, model.meta)
        inputs.append(torch.jit.Tuple([state]))

    sequences = [prompt[:] for _ in range(param.batch_size)]

    num_steps = 0
    while not sample_control[0].finished:
        sample_inner(sample_control, sequences, model.model, inputs, param)
        num_steps += 1

        # Terminate if maximum steps have been reached
        if param.max_steps > 0 and num_steps >= param.max_steps:
            terminated = True
            break

    output = [None] * param.batch_size
    if not terminated:
        sample_control[0].enc.tokens_to_json_array(sequences, output)
        sample_control[0].finalize(output[0])  # Finalize only the first output, assuming batch size is 1

    return output

def sample_step(piece: Piece, status: Status, param: SampleParam, model: torch.ScriptModule, step: Step):
    """
    Executes a sampling step where new bars are generated based on a specific section of a piece.
    The function modifies `piece` in-place by inserting newly generated tracks/bars.
    """
    track_set = set()
    bars_to_generate = set()
    bar_mapping = []
    track_count = 0
    num_tracks = len(step.step)

    for i in range(num_tracks):
        track_used = False
        for j in range(step.start, step.end):
            if step.step[i][j]:
                bars_to_generate.add((track_count, j - step.start))
                bar_mapping.append((track_count, j - step.start, i, j))
            if step.step[i][j] or step.context[i][j]:
                track_set.add(i)
                track_used = True
        if track_used:
            track_count += 1

    tracks = list(track_set)

    step_status = status_subset(status, step.start, step.end, tracks)
    if bars_to_generate:
        status_rehighlight(step_status, bars_to_generate)

    step_piece = piece_subset(piece, step.start, step.end, tracks)
    gen_piece = generate(step_piece, step_status, param, model)

    piece_insert(piece, gen_piece, bar_mapping, param.verbose)

    update_status_instruments(piece, status)
    override_piece_features(piece, status)


def sample(piece: Piece, status: Status, param: SampleParam):
    model = ModelMeta()
    model.model = torch.jit.load(param.ckpt)
    model.meta.model_dim = param.model_dim
    encoder = TrackDensityEncoder()

    # TODO:
    # pad_piece_with_status
    # add_timesigs_to_status
    # override_piece_features

    selection_mask = status_to_selection_mask(status)
    if (not any(selection_mask)):
        return

    resample_mask = status_to_resample_mask(status)
    ignore_mask = status_to_ignore_mask(status)

    steps = find_steps(selection_mask, resample_mask, ignore_mask, param)
    if (len(steps) == 0):
        return

    # TODO: ordering and reordering of tracks (?)
    for step in steps:
        sample_step(piece, status, param, model, step)

    return piece


def sample_multi_step(piece_json: str, status_json: str, param_json: str):
    """ Generates output from model """
    piece = Piece(**json.loads(piece_json))
    status = Status(**json.loads(status_json))
    param = SampleParam(**json.loads(param_json))

    output_str = sample(piece, status, param)
    return json.dumps(output_str)

# TODO: from this generated input we would like to have midi file

# maybe some cpp can be reused - like through "py::class_"