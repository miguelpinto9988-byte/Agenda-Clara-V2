#!/usr/bin/env python3
"""Structural regression guards; Go and Android tests run separately in CI."""
from pathlib import Path
p = Path("AgendaClara")
go = (p / "whatsapp-native/main.go").read_text(encoding="utf-8")
java = (p / "app/src/main/java/pe/agendaclara/app/WhatsAppSessionService.java").read_text(encoding="utf-8")
tests = (p / "whatsapp-native/main_test.go").read_text(encoding="utf-8")
gradle = (p / "app/build.gradle").read_text(encoding="utf-8")
assert 'case *events.PairError:' in go and '"error_code": "pair_finish_failed"' in go
assert '"error_code": "connection_rejected"' in go
assert '"error_code": "temporary_restriction"' in go
assert 'if t.client != nil && t.client.Store.ID == nil {' in go
assert 'func TestPairingErrorsInvalidateStaleCode' in tests
assert '.remove("wa_pair_code").remove("wa_pair_expires")' in java
assert "versionCode 46" in gradle and "versionName '3.10.5'" in gradle
print("PASS: structural 3.10.5 WhatsApp regression checks")
