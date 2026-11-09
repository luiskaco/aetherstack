"""
AetherStack - Virtual hosts de Nginx (solo biblioteca estándar, sin efectos secundarios).

Genera la configuración de un proyecto y valida el dominio de desarrollo (.local, .test...).
Está separado de core.py para poder probarse sin tocar la instalación.
"""
import re

DEFAULT_TLD = "local"
_TLD_RE = re.compile(r"^[a-z]{2,10}$")

VHOST_TEMPLATE = """# Virtual host para {name}
server {{
    listen 127.0.0.1:{port};
    server_name {domain};

    root "{root}";
    index index.php index.html;

    location / {{
        try_files $uri $uri/ /index.php?$query_string;
    }}

    location ~ \\.php$ {{
        try_files $uri =404;
        fastcgi_split_path_info ^(.+\\.php)(/.+)$;
        fastcgi_pass php_cgi;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include "{fastcgi_params}";
        fastcgi_read_timeout 300;
    }}

    location ~ /\\. {{
        deny all;
    }}
}}
"""


def normalize_tld(value):
    """Devuelve el dominio válido (minúsculas, sin punto) o DEFAULT_TLD si el valor no sirve."""
    value = str(value or "").strip().lower().lstrip(".")
    return value if _TLD_RE.match(value) else DEFAULT_TLD


def domain_for(project_name, tld):
    return f"{project_name}.{normalize_tld(tld)}"


def render_vhost(name, root, port, fastcgi_params, tld=DEFAULT_TLD):
    return VHOST_TEMPLATE.format(name=name, domain=domain_for(name, tld), root=root,
                                 port=port, fastcgi_params=fastcgi_params)
