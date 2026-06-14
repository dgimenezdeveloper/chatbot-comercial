#!/bin/bash

# Evitamos duplicar la configuración si el script se corre varias veces
if ! grep -q "parse_git_branch" ~/.bashrc; then
  # Función para detectar la rama de Git
  echo "parse_git_branch() { git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/ (\1)/'; }" >> ~/.bashrc
  
  # PS1 con el esquema de colores exacto de Ubuntu (Verde para usuario, Azul para ruta, Amarillo para Git)
  echo 'export PS1="\[\e[01;32m\]\u@\h\[\e[00m\]:\[\e[01;34m\]\w\[\e[01;33m\]\$(parse_git_branch)\[\e[00m\]\$ "' >> ~/.bashrc
fi