#!/usr/bin/env python3
"""Structural regression guards. Go tests and Android APK build remain mandatory."""
from pathlib import Path
r = Path("AgendaClara")
go = (r / "whatsapp-native/main.go").read_text(encoding="utf-8")
java = (r / "app/src/main/java/pe/agendaclara/app/WhatsAppSessionService.java").read_text(encoding="utf-8")
tests = (r / "whatsapp-native/main_test.go").read_text(encoding="utf-8")
gradle = (r / "app/build.gradle").read_text(encoding="utf-8")

assert "if cli.IsLoggedIn() {" in go
assert "if cli.IsConnected() {" in go and "cli.Disconnect()" in go
assert "pairGeneration uint64" in go and "t.cancelPair()" in go
assert '"socket_connected": cli.IsConnected()' in go
assert '"already_processed": true' in go
assert "worker.shutdown();" in java and "worker.shutdownNow();" not in java
assert 'reconcile(WhatsAppNative.call(request("status")))' in java
assert 'JSONObject status=WhatsAppNative.call(request("connect")' in java
assert "TestPairGenerationSuppressesStaleEvents" in tests
assert "TestHistoryRefreshCompletesWhenAlreadyProcessed" in tests
assert "versionName '3.10.4'" in gradle and "versionCode 45" in gradle
print("PASS: structural WhatsApp regression checks for candidate 3.10.4")
