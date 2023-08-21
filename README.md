<div align="center">
  <a href="https://github.com/tom-bartk/pyllot">
    <img src="https://pyllot.tombartk.com/images/logo.png" alt="Logo" width="326" height="99">
  </a>

<div align="center">
<a href="https://jenkins.tombartk.com/job/pyllot/">
  <img alt="Jenkins" src="https://img.shields.io/jenkins/build?jobUrl=https%3A%2F%2Fjenkins.tombartk.com%2Fjob%2Fpyllot">
</a>
<a href="https://jenkins.tombartk.com/job/pyllot/lastCompletedBuild/testReport/">
  <img alt="Jenkins tests" src="https://img.shields.io/jenkins/tests?jobUrl=https%3A%2F%2Fjenkins.tombartk.com%2Fjob%2Fpyllot">
</a>
<a href="https://jenkins.tombartk.com/job/pyllot/lastCompletedBuild/coverage/">
  <img alt="Jenkins Coverage" src="https://img.shields.io/jenkins/coverage/apiv4?jobUrl=https%3A%2F%2Fjenkins.tombartk.com%2Fjob%2Fpyllot%2F">
</a>
<a href="https://www.gnu.org/licenses/agpl-3.0.en.html">
  <img alt="PyPI - License" src="https://img.shields.io/pypi/l/pyllot">
</a>
<a href="https://pypi.org/project/pyllot/">
  <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/pyllot">
</a>
<a href="https://pypi.org/project/pyllot/">
  <img alt="PyPI - Version" src="https://img.shields.io/pypi/v/pyllot">
</a>
<a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff" style="max-width:100%;"></a>
</div>

  <p align="center">
    Application routing with event-driven finite-state machine.
    <br />
    <a href="https://pyllot.tombartk.com"><strong>Documentation</strong></a>
  </p>
</div>

## Simple example

```python3
# main.py

from typing import NamedTuple

from pyllot import (
    Router,
    ScreenBase,
    ScreenPresenting,
    ScreensFactoryBase,
    Transition,
    TransitionDirection,
)


class MyScreen(ScreenBase):
    def will_present(self) -> None:
        print(f'Will present "{self.screen_name}"')

    def did_present(self) -> None:
        print(f'Did present "{self.screen_name}"')

    def will_disappear(self) -> None:
        print(f'Will disappear "{self.screen_name}"')


class HomeScreen(MyScreen):
    @property
    def screen_name(self) -> str:
        return "home"


class VideoPlayerScreen(MyScreen):
    @property
    def screen_name(self) -> str:
        return "video_player"


class State(NamedTuple):
    current_video_url: str | None


def has_current_video(state: State) -> bool:
    return state.current_video_url is not None


class MyPresenter(ScreenPresenting[MyScreen]):
    def present(self, screen: MyScreen) -> None:
        print(f'Presenting "{screen.screen_name}"')


class MyScreensFactory(ScreensFactoryBase[MyScreen]):
    def create(self, screen_name: str) -> MyScreen:
        print(f'Creating screen "{screen_name}"')
        match screen_name:
            case "home":
                return HomeScreen()
            case "video_player":
                return VideoPlayerScreen()
            case _:
                raise NotImplementedError


HOME_TO_VIDEO_PLAYER: Transition[State] = Transition(
    source="home",
    destination="video_player",
    direction=TransitionDirection.PUSH,
    condition=has_current_video,
)

VIDEO_PLAYER_TO_HOME: Transition[State] = Transition(
    source="video_player",
    destination="home",
    direction=TransitionDirection.POP,
    condition=lambda state: not has_current_video(state),
)


def main() -> None:
    router: Router[State, MyScreen] = Router(
        initial_screen=HomeScreen(),
        presenter=MyPresenter(),
        screens_factory=MyScreensFactory(),
    )
    router.add_transition(
        Transition(
            source="home",
            destination="video_player",
            direction=TransitionDirection.PUSH,
            condition=has_current_video,
        )
    )
    router.add_transition(
        Transition(
            source="video_player",
            destination="home",
            direction=TransitionDirection.POP,
            condition=lambda state: not has_current_video(state),
        )
    )
    print("Presenting video player...")
    router.on_state(State(current_video_url="https://tombartk.com/funny_cats.mp4"))

    print("\nGoing back to home screen...")
    router.on_state(State(current_video_url=None))


if __name__ == "__main__":
    main()
```

```sh
$ python3 main.py

Presenting video player...
Creating screen "video_player"
Will disappear "home"
Will present "video_player"
Presenting "video_player"
Did present "video_player"

Going back to home screen...
Will disappear "video_player"
Will present "home"
Presenting "home"
Did present "home"
```

## Installation

Pyllot is available as [`pyllot`](https://pypi.org/project/pyllot/) on PyPI:

```shell
pip install pyllot
```

## Usage

For detailed quickstart and API reference, visit the [Documentation](https://pyllot.tombartk.com/quickstart/).


## License
![AGPLv3](https://www.gnu.org/graphics/agplv3-with-text-162x68.png)
```monospace
Copyright (C) 2023 tombartk 

This program is free software: you can redistribute it and/or modify it under the terms
of the GNU Affero General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program.
If not, see https://www.gnu.org/licenses/.
```
