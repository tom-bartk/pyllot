## Define the Screens
A [`Screen`](/api/screen/#pyllot.abc.ScreenBase) is the root widget of some standalone part of the application. Pyllot navigates between screens by performing transitions.

Following example defines a base `MyScreen` class for all screens of the application, and
two concrete screens - `HomeScreen`, and `VideoPlayerScreen`.


```python3
import pyllot


class MyScreen(pyllot.ScreenBase):
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
```

It's important to pick a unique name for each screen subclass. Doing so ensures that the transitions are predictable.

## Create a Screens Factory

A [`ScreensFactory`](/api/factory/#pyllot.abc.ScreensFactoryBase) will create new screens at runtime, instead of having to instantiate all screens at startup.

Following example defines a simple screens factory based on screens from the previous example:

```python3
import pyllot

...

class MyScreensFactory(pyllot.ScreensFactoryBase[MyScreen]):
    def create(self, screen_name: str) -> MyScreen:
        match screen_name:
            case "home":
                return HomeScreen()
            case "video_player":
                return VideoPlayerScreen()
            case _:
                raise NotImplementedError
```
## Define the State

A state is an object that keeps track of some properties of a system. Pyllot relies on state changes to evaluate whether a given transition should be performed.

Following example defines a state class that tracks an URL of the currently selected video:

```python3
from typing import NamedTuple


class State(NamedTuple):
    current_video_url: str | None
```

## Add Transitions
A [`Transition`](/api/transition/#pyllot.Transition) describes a possible navigation from one screen to another. 

A transition has a [`TransitionDirection`](/api/direction/#pyllot.direction.TransitionDirection):

- [`TransitionDirection.PUSH`](/api/direction/#pyllot.direction.TransitionDirection.PUSH) - create a new screen and push it on the navigation stack,
[`TransitionDirection.POP`](/api/direction/#pyllot.direction.TransitionDirection.POP) - "go back" to the previous screen by removing screen(s) from the navigation stack.

Every transition has a condition based on the state, which when evaluated as true, will cause the transition to be performed.

Following example defines a `has_current_video` condition and two transitions:

```python3
import pyllot

...

def has_current_video(state: State) -> bool:
    return state.current_video_url is not None


HOME_TO_VIDEO_PLAYER: pyllot.Transition[State] = pyllot.Transition(
    source="home",
    destination="video_player",
    direction=pyllot.TransitionDirection.PUSH,
    condition=has_current_video,
)


VIDEO_PLAYER_TO_HOME: pyllot.Transition[State] = pyllot.Transition(
    source="video_player",
    destination="home",
    direction=pyllot.TransitionDirection.POP,
    condition=lambda state: not has_current_video(state),
)
```

Now when router displays the `HomeScreen` and the new state has a video url, the `HOME_TO_VIDEO_PLAYER` transition is performed. To "go back", the video url of the state has to change to `None`.


## Create a Presenter

A [`Presenter`](/api/presenter/#pyllot.abc.ScreenPresenting) is an object responsible for displaying the screen to the end user. The exact implementation will vary depending on the presentation framework.

Following example defines a presenter that prints the name of the screen to present:

```python3
import pyllot

...

class MyPresenter(pyllot.ScreenPresenting[MyScreen]):
    def present(self, screen: MyScreen) -> None:
        print(f'Presenting "{screen.screen_name}"')
```

The `pyllot.ScreenPresenting[MyScreen]` does not need to be included in the MRO, as the typing of the presenter is checked structurally.

## Create the Router

The [`Router`](/api/router/#pyllot.Router) is the main object that manages the transitions between screens.

It's designed as a finite-state machine, where nodes are the screens, and the transitions are represented by the [`Transition`](/api/transition/#pyllot.Transition) objects.

Navigation is triggered whenever the application's state changes, and one of the registered transitions evaluates it's predicate as true.

Following example creates a router using the previously defined factory and the presenter, and adds the `HOME_TO_VIDEO_PLAYER` and the `VIDEO_PLAYER_TO_HOME` transitions:

```python3
import pyllot

...

def main() -> None:
    router: pytllot.Router[State, MyScreen] = pyllot.Router(
        initial_screen=HomeScreen(),
        presenter=MyPresenter(),
        screens_factory=MyScreensFactory(),
    )

    router.add_transition(HOME_TO_VIDEO_PLAYER)
    router.add_transition(VIDEO_PLAYER_TO_HOME)
```

## Perform a Transition

The final step is to perform the transition from the `HomeScreen` to the `VideoPlayerScreen`.

To do that, trigger a state change on the router. In this case, the new `State` has to have a non-empty video URL, so that the `has_current_video` predicate evaluates as true.

Following example performs a transition from `HomeScreen` to `VideoPlayerScreen`:

```python3
def main() -> None:
    ...
    print("Presenting video player...")
    router.on_state(State(current_video_url="https://tombartk.com/funny_cats.mp4"))

```

Running the script will result in the following output:

```sh
$ python3 main.py

Presenting video player...
Creating screen "video_player"
Will disappear "home"
Will present "video_player"
Presenting "video_player"
Did present "video_player"
```

<hr/>
To learn more, see the [API Documentation](/api/router/).
<br/>
