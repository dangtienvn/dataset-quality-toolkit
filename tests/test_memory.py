from saas_starter.copilot.memory import ConversationMemory

def test_memory():
    mem = ConversationMemory(max_history=2)
    mem.add_message("user", "m1")
    mem.add_message("assistant", "m2")
    mem.add_message("user", "m3")
    assert len(mem.history) == 2
