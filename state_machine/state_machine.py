#!/usr/bin/env python

import logging
import time
import transitions
from transitions import Machine

evsm_states = ['active', 'inactive', 'discarding']
evsm_events = ['switch_reconciling', 'reconcile_complete', 'event_rx']

evsm_transitions = [
    [ 'switch_reconciling', 'active',     'inactive'],
    [ 'reconcile_complete', 'inactive',   'active',     None, None, '_drain_queue'],
    [ 'event_rx',           'active',     None,     None, None, '_handle_event'],
    [ 'event_rx',           'inactive',   None,   None, None, '_queue_event'],
    [ 'event_rx',           'discarding', None, None, None, '_log_event_error'],
]

pssm_states = ['uninitialized', 'reconciling', 'reconciled', 'reconcile_failed']
pssm_events = ['reconcile', 'reconcile_success', 'reconcile_fail', 'audit']

pssm_transitions = [
    ['reconcile',         'uninitialized',    'reconciling',      None, None, None, '_do_reconcile'],
    ['reconcile_success', 'reconciling',      'reconciled',       None, None, '_reconcile_complete'],
    ['reconcile_failed',  'reconciling',      'reconcile_failed', None, None, '_reconcile_failed'],
    ['audit',             'reconcile_failed', 'reconciling',      None, None, None, '_do_reconcile'],
]

class CxMacAttachmentsEventSm(Machine):
    def __init__(self):
        print 'Initializing Event handling SM'
        Machine.__init__(self, states=evsm_states, transitions=evsm_transitions, initial='active',
                        ignore_invalid_triggers=True)

    def _handle_event(self, *args, **kwargs):
        event = kwargs['event']
        print 'Handling event: {}'.format(event)

    def _drain_queue(self, *args, **kwargs):
        print 'Draining queue'

    def _queue_event(self, *args, **kwargs):
        event = kwargs['event']
        print 'Queueing event {}'.format(event)

    def _log_event_error(self, *args, **kwargs):
        event = kwargs['event']
        print 'Could not handle event: {} in current state'.format(event)

class CxMacAttachmentsPssm(Machine):
    def __init__(self, name, event_handler):
        print 'Initializing PSSM for: {}'.format(name)
        self._name = name
        self._event_handler = event_handler
        Machine.__init__(self, states=pssm_states, transitions=pssm_transitions, initial='uninitialized',
                        ignore_invalid_triggers=True, name=name)

    def _reconcile_complete(self, *args, **kwargs):
        print 'In reconcile completed'
        self._event_handler.reconcile_complete()

    def _reconcile_failed(self, *args, **kwargs):
        print 'Reconcile failed'
        self._event_handler.reconcile_complete()

    def _do_reconcile(self, *args, **kwargs):
        try:
            print 'Starting reconciliation for switch: {}'.format(self._name)
            self._event_handler.switch_reconciling()
            time.sleep(1)
            raise ValueError('Failed')
            print 'Reconcile complete for switch: {}'.format(self._name)
            self.reconcile_success()
        except Exception:
            self.reconcile_failed()

class CxMacAttachments(object):
    _switches = dict()
    _event_handler = CxMacAttachmentsEventSm()

    def __init__(self):
        print 'Initializing'

    def discovered(self, switch):
        pssm = CxMacAttachmentsPssm(switch, CxMacAttachments._event_handler)
        print 'Discovered switch: {}'.format(switch)
        CxMacAttachments._switches[switch] = pssm

    def rx_event(self, event):
        CxMacAttachments._event_handler.event_rx(event=event)

    def verify_switch(self, switch):
        pssm = CxMacAttachments._switches[switch]
        pssm.audit()

    def synchronize_switch(self, switch):
        pssm = CxMacAttachments._switches[switch]
        print 'Before state = {}'.format(pssm.state)
        pssm.reconcile()
        print 'After state = {}'.format(pssm.state)

def main():
    print 'In main'

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('transitions').setLevel(logging.INFO)

    switch1 = 'switch-1'
    cx_ma = CxMacAttachments()
    cx_ma.discovered(switch1)

    cx_ma.synchronize_switch(switch1)
    cx_ma.rx_event(dict(state='remove'))

    cx_ma.verify_switch(switch1)
    cx_ma.rx_event(dict(state='add'))

if __name__ == '__main__':
    main()
