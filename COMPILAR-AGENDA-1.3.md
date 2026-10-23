# Compilación de Agenda Clara 1.3.0

El archivo [`.github/workflows/compilar-apk.yml`](.github/workflows/compilar-apk.yml) ya está configurado para compilar en GitHub Actions con Gradle 8.9, JDK 17 y Android SDK 35.

## Para preparar una compilación real

1. Subir al directorio raíz de este repositorio **exactamente** `Agenda-Clara-1.3.0-Fuentes-Sin-Clave.zip`. No subir otro ZIP que contenga `.jks`, `.keystore`, contraseñas o credenciales.
2. Abrir `Settings > Secrets and variables > Actions > New repository secret`. Crear `SIGNING_JKS_BASE64` con la representación Base64 de la clave `AgendaClara/signing/development.jks` del respaldo local original; **no subir la clave** a este repositorio público.
3. Ir a `Actions > Compilar Agenda Clara 1.3.0 > Run workflow`, o volver a subir un ZIP actualizado al directorio raíz.
4. Al finalizar en verde, abrir la ejecución y descargar el artefacto `Agenda-Clara-1.3.0-APK`. Dentro estará `app-debug.apk`.

Para convertir una clave a Base64 en Windows PowerShell:

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\ruta\al\development.jks"))
```

La compilación confirma integridad ZIP, compila con `./gradlew :app:assembleDebug`, verifica con `apksigner` y compara el certificado. Si GitHub informa errores, revisar la sección `Actions` de la ejecución. No desinstalar la app existente si se quieren conservar datos; verificar compatibilidad de firma y versión antes de actualizar.

**Estado:** preparado para compilar, pero no implica una APK creada ni instalación verificada.
