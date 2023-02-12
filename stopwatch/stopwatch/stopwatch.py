"""A Pynecone example of a stopwatch."""
import pynecone as pc
from datetime import datetime, timedelta
import asyncio

class State(pc.State):
    is_starting: bool = False
    is_stoping: bool = False
    start_time: str 
    end_time: str
    total_delta_seconds: int = 0
    total_delta_microseconds: int = 0

    @pc.var
    def current_time(self):
        return datetime.now().isoformat()

    @pc.var
    def time_delta(self)->str:
        if not self.end_time and not self.start_time:
            delta = timedelta(0)
        elif not self.end_time:
            delta = datetime.fromisoformat(self.current_time) - datetime.fromisoformat(self.start_time)
        else:
            delta = datetime.fromisoformat(self.end_time) - datetime.fromisoformat(self.start_time)
        return delta.seconds, delta.microseconds

    @pc.var
    def current_time_delta_microseconds(self):
        _ , microseconds = self.time_delta
        return microseconds

    @pc.var
    def current_time_delta_seconds(self)->int:
        seconds , _ = self.time_delta
        return seconds

    @pc.var
    def time_delta_calc(self):
        microseconds = self.total_delta_microseconds
        seconds = self.total_delta_seconds
        if self.is_starting:
            microseconds += self.current_time_delta_microseconds
            seconds += self.current_time_delta_seconds
        if microseconds >= 1000000:
            microseconds -= 1000000
            seconds += 1
        minutes = int((seconds % 3600) / 60)
        seconds = seconds % 60
        return minutes, seconds, microseconds

    @pc.var
    def current_total_time(self):
        minutes, seconds, microseconds = self.time_delta_calc
        return f"{str(minutes).rjust(2, '0')}:{str(seconds).rjust(2,'0')}.{str(microseconds)[:2].ljust(2,'0')}"

    async def inf_loop(self):
        if self.is_starting:
            await asyncio.sleep(0.005)
            return self.inf_loop

    def start(self):
        if self.is_stoping:
            self.is_stoping = False
            self.end_time = None
        self.is_starting = True
        self.start_time = datetime.now().isoformat()
        self.is_starting = True
        return self.inf_loop

    def stop(self):
        self.is_starting = False
        self.is_stoping = True
        self.total_delta_seconds += self.current_time_delta_seconds
        self.total_delta_microseconds += self.current_time_delta_microseconds
        if self.total_delta_microseconds >= 1000000:
            self.total_delta_microseconds -= 1000000
            self.total_delta_seconds += 1
        self.end_time = datetime.now().isoformat()

    def reset(self):
        self.is_starting = False
        self.is_stoping = False
        self.end_time = None
        self.start_time = None
        self.total_delta_microseconds = 0
        self.total_delta_seconds = 0

def start_button():
    return pc.button(
        "Start",
        color="black",
        bg="orange",
        border_radius="50%",
        height="4em",
        width="4em",
        font_size="2em",
        on_click=State.start,
    )

def stop_button():
    return pc.button(
        "Stop",
        color="black",
        bg="orange",
        border_radius="50%",
        height="4em",
        width="4em",
        font_size="2em",
        on_click=State.stop,
    )

def reset_button():
    return pc.button(
        "Reset",
        color="black",
        bg="gray",
        border_radius="50%",
        height="4em",
        width="4em",
        font_size="2em",
        on_click=State.reset,
    )

def time():
    return pc.vstack(
        pc.text(
            State.current_total_time,
            color="black",
            font_size="5em",
        ),
    )

def index():
    """The main view."""
    return pc.center(
        pc.vstack(
            pc.circle(
                time(),
                width="25em",
                height="25em",
                padding="5em",
                border_width="medium",
                border_color="#43464B",
                border_radius="50%",
                bg="#ededed",
                text_align="center",
            ),
            pc.hstack(
                reset_button(),
                pc.cond(
                    State.is_starting,
                    stop_button(),
                    start_button(),
                ),
                template_columns="repeat(2, 1fr)",
                gap=200,
            ),
            padding="5em",
        )
    )

# Add state and page to the app.
app = pc.App(state=State)
app.add_page(index, title="Stopwatch")
app.compile()
