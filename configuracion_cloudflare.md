# Solución para el error 403 Forbidden en Cloudflare

## El problema

El error 403 Forbidden ocurre porque Cloudflare está bloqueando las solicitudes a tu backend. Esto puede deberse a varias razones:

1. **Configuración incorrecta en Cloudflare**: El nivel de seguridad es demasiado estricto.
2. **Firewall de Cloudflare**: Algunas reglas de firewall están bloqueando las solicitudes.
3. **Protección de bot**: Cloudflare detecta que las solicitudes no son de un navegador normal.

## Solución 1: Ajustar la configuración de Cloudflare

1. Inicia sesión en tu cuenta de Cloudflare
2. Selecciona el dominio vokaflow.com
3. Ve a la sección "Seguridad" > "Configuración"
4. Cambia el nivel de seguridad a "Bajo" o "Estándar"
5. Desactiva "Bot Fight Mode" y "Challenge Passage" temporalmente

## Solución 2: Verificar las reglas de Page Rules

1. Ve a la sección "Reglas" > "Page Rules"
2. Verifica que no haya reglas que estén bloqueando el subdominio backend.vokaflow.com
3. Considera crear una regla específica para el subdominio:
   - URL: `*backend.vokaflow.com/*`
   - Configuración: "Security Level: Essentially Off"
   - Configuración: "Browser Integrity Check: Off"

## Solución 3: Configurar correctamente el DNS

1. Ve a la sección "DNS" > "Registros"
2. Busca el registro para "backend" o "api_backend"
3. Asegúrate de que:
   - Sea un registro tipo A
   - Apunte a tu IP pública: 82.198.224.134
   - El proxy esté activado (nube naranja)

## Solución 4: Configuración SSL/TLS

1. Ve a la sección "SSL/TLS"
2. En "Modo de encriptación", selecciona "Flexible"
3. En "Edge Certificates", asegúrate de que "Always Use HTTPS" esté activado

## Solución 5: Revisar en el panel de Cloudflare

1. Ve a la sección "Overview" o "Analytics"
2. Mira si hay solicitudes bloqueadas o desafíos presentados
3. Comprueba los registros de firewall para ver exactamente qué está siendo bloqueado

## Pasos adicionales para depuración

Si después de realizar estos cambios sigues experimentando el error 403, puedes:

1. Desactivar temporalmente Cloudflare (cambia el proxy a "DNS only" - nube gris)
2. Intentar acceder directamente a tu servidor usando la IP: http://82.198.224.134:80
3. Revisar los logs de Nginx en tu servidor:
   ```bash
   sudo tail -f /var/log/nginx/api-access.log
   sudo tail -f /var/log/nginx/api-error.log
   ```

## Notas importantes

- Los cambios en Cloudflare pueden tardar unos minutos en propagarse
- Algunas configuraciones avanzadas de seguridad pueden requerir un plan pagado de Cloudflare
- Si estás usando Cloudflare Workers o funciones específicas, estas también pueden interferir con el acceso 