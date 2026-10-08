p = "frontend/src/components/domain/GestorProgramacion.tsx"
s = open(p, encoding="utf-8").read()
a = ("                    } }));\n"
     "                }\n"
     "            }\n"
     "        } catch (err) {\n"
     "            console.error('Error generando programación:', err);\n")
assert s.count(a) == 1, s.count(a)
b = ("                    } }));\n"
     "                }\n"
     "                // GAN2 (cajita = viaje): la respuesta de POST /generar trae las tareas POR ETIQUETA; la agrupacion por\n"
     "                // viaje se hace en GET /api/programacion (backend, al leer). Sin esta relectura, tras pulsar \"Generar\" el\n"
     "                // Gantt y la Bolsa quedaban dibujando 1 cajita por etiqueta hasta el siguiente refresco (F5).\n"
     "                await fetchData(true);\n"
     "            }\n"
     "        } catch (err) {\n"
     "            console.error('Error generando programación:', err);\n")
s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("OK handleGenerar parcheado")
