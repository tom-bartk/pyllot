from unittest.mock import Mock

from src.pyllot import Transition, TransitionDirection


class TestTransition:
    def test_source__returns_value_passed_to_init(self):
        sut = Transition(
            source="foo",
            destination="bar",
            direction=TransitionDirection.PUSH,
            condition=Mock(),
        )
        assert sut.source == "foo"

    def test_destination__returns_value_passed_to_init(self):
        sut = Transition(
            source="foo",
            destination="bar",
            direction=TransitionDirection.PUSH,
            condition=Mock(),
        )
        assert sut.destination == "bar"

    def test_direction__returns_value_passed_to_init(self):
        sut = Transition(
            source="foo",
            destination="bar",
            direction=TransitionDirection.POP,
            condition=Mock(),
        )
        assert sut.direction == TransitionDirection.POP

    def test_should_transition__returns_result_of_condition_passed_to_init(self):
        expected = True
        condition = Mock(return_value=expected)
        sut = Transition(
            source="foo",
            destination="bar",
            direction=TransitionDirection.POP,
            condition=condition,
        )

        result = sut.should_transition(Mock())

        assert result == expected

    def test_should_transition__calls_condition_passed_to_init_with_state_param(self):
        state = Mock()
        condition = Mock()
        sut = Transition(
            source="foo",
            destination="bar",
            direction=TransitionDirection.POP,
            condition=condition,
        )

        sut.should_transition(state=state)

        condition.assert_called_once_with(state)
