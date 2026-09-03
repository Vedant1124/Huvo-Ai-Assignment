from backend.agent import Agent
from backend.models import ChatMessage, CustomerState, Role


def test_agent_respects_do_not_contact():
    agent = Agent()

    state = CustomerState(do_not_contact=True)

    history = [
        ChatMessage(
            role=Role.user,
            content="Please don't contact me again."
        )
    ]

    reply, updated_state = agent.generate(history, state)

    assert updated_state.do_not_contact is True
    assert "contact" in reply.lower()


def test_agent_respects_escalation():
    agent = Agent()

    state = CustomerState(escalation_required=True)

    history = [
        ChatMessage(
            role=Role.user,
            content="Connect me with a representative."
        )
    ]

    reply, updated_state = agent.generate(history, state)

    assert updated_state.escalation_required is True
    assert "contact you soon" in reply.lower()