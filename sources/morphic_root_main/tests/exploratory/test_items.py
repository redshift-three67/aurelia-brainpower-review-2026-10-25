#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test ob items group und rates haben"""

from services.subgroup_service import SubgroupService

svc = SubgroupService()
items = svc.generate_fullbody_candidates(['endokrin', 'meridiane'], 'test', k_total=4)

print(f"Anzahl Items: {len(items)}")
for i, item in enumerate(items):
    label = item.get('label', 'NO_LABEL')
    group = item.get('group', 'NO_GROUP')
    rates = item.get('rates', [])
    print(f"{i+1}. {label} | group={group} | rates={len(rates)} items")
    if rates:
        print(f"   rates: {rates}")
