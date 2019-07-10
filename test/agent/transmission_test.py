from test.base import *

class TestTransmission(object):

    def setup(self):
        reset_simulation()
        self.source_agent = Agent('source', 0.5)
        self.transmission = Transmission('transmission', self.source_agent, current_time())
        self.near_target = Agent('near', 0.4)
        self.far_target = Agent('far', 0.9)
        add_agent(self.source_agent)
        add_agent(self.transmission)
        add_agent(self.near_target)
        add_agent(self.far_target)

    def test_receive(self):
        other_transmission = Transmission('other-transmission', self.near_target, current_time())
        self.transmission.receive(other_transmission, current_time() + 0.1)
        assert len(self.transmission.transmissions_received) == 0

    def test_advance_once_without_reaching_any_targets(self):
        with patch.object(self.transmission, 'receive') as transmission_receive:
            with patch.object(self.source_agent, 'receive') as source_agent_receive:
                with patch.object(self.near_target, 'receive') as near_target_receive:
                    with patch.object(self.far_target, 'receive') as far_target_receive:
                        advance_time(0.09)
                        assert not transmission_receive.called
                        assert not source_agent_receive.called
                        assert not near_target_receive.called
                        assert not far_target_receive.called

    def test_advance_once_reaching_near_target(self):
        with patch.object(self.transmission, 'receive') as transmission_receive:
            with patch.object(self.source_agent, 'receive') as source_agent_receive:
                with patch.object(self.near_target, 'receive') as near_target_receive:
                    with patch.object(self.far_target, 'receive') as far_target_receive:
                        advance_time(0.11)
                        assert not transmission_receive.called
                        assert not source_agent_receive.called
                        assert near_target_receive.called
                        assert not far_target_receive.called

    def test_advance_once_reaching_both_targets(self):
        with patch.object(self.transmission, 'receive') as transmission_receive:
            with patch.object(self.source_agent, 'receive') as source_agent_receive:
                with patch.object(self.near_target, 'receive') as near_target_receive:
                    with patch.object(self.far_target, 'receive') as far_target_receive:
                        advance_time(0.45)
                        assert not transmission_receive.called
                        assert not source_agent_receive.called
                        assert near_target_receive.called
                        assert far_target_receive.called
                        # FIXME how to assert near target was called first?

    def test_advance_twice_reaching_each_target_in_turn(self):
        advance_time(0.11)
        with patch.object(self.transmission, 'receive') as transmission_receive:
            with patch.object(self.source_agent, 'receive') as source_agent_receive:
                with patch.object(self.near_target, 'receive') as near_target_receive:
                    with patch.object(self.far_target, 'receive') as far_target_receive:
                        advance_time(0.34)
                        assert not transmission_receive.called
                        assert not source_agent_receive.called
                        assert not  near_target_receive.called
                        assert far_target_receive.called

    def test_advance_once_reaching_near_target_at_double_speed(self):
        self.transmission.speed = 2.0
        with patch.object(self.transmission, 'receive') as transmission_receive:
            with patch.object(self.source_agent, 'receive') as source_agent_receive:
                with patch.object(self.near_target, 'receive') as near_target_receive:
                    with patch.object(self.far_target, 'receive') as far_target_receive:
                        advance_time(0.055)
                        assert not transmission_receive.called
                        assert not source_agent_receive.called
                        assert near_target_receive.called
                        assert not far_target_receive.called

    def test_transmission_removes_itself_from_simulation_after_reaching_boundary(self):
        assert get_agent(self.transmission.id) is not None
        advance_time(0.6)
        with raises(KeyError):
            get_agent(self.transmission.id)
