import tempfile
from note_seq import midi_io, plot_sequence
from fastapi.responses import HTMLResponse
from bokeh.embed import file_html
from bokeh.resources import CDN
from bokeh.io import curdoc


async def handle_get_painoroll(file):
    """
    Returns HTML pianoroll of the provided midi file

    Args:
        file (UploadFile): An uploaded MIDI file to be processed.

    Returns:
        HTMLResponse: A response containg pianoroll of the file.
    """

    with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as temp_file:
        temp_file.write(await file.read())
        temp_filepath = temp_file.name

    note_sequence = midi_io.midi_file_to_note_sequence(temp_filepath)
    doc = curdoc()
    doc.clear()
    plot_sequence(note_sequence)

    html_content = file_html(doc, CDN, "Piano Roll Visualization")

    return HTMLResponse(content=html_content)
