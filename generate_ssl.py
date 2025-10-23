#!/usr/bin/env python
"""
Gerador de certificados SSL para desenvolvimento local
"""
import os
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime

def create_ssl_certificate():
    """Cria certificado SSL auto-assinado para desenvolvimento"""
    
    print("=== CRIANDO CERTIFICADO SSL ===")
    
    # Gerar chave privada
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Criar certificado
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "BR"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "SP"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "São Paulo"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Central MEI"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.DNSName("127.0.0.1"),
            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    # Criar diretório ssl se não existir
    ssl_dir = "ssl"
    os.makedirs(ssl_dir, exist_ok=True)
    
    # Salvar chave privada
    with open(os.path.join(ssl_dir, "key.pem"), "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # Salvar certificado
    with open(os.path.join(ssl_dir, "cert.pem"), "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    print("✅ Certificado SSL criado com sucesso!")
    print(f"📁 Arquivos salvos em: {os.path.abspath(ssl_dir)}")
    print("🔐 cert.pem - Certificado público")
    print("🔑 key.pem - Chave privada")
    
    return os.path.abspath(os.path.join(ssl_dir, "cert.pem")), os.path.abspath(os.path.join(ssl_dir, "key.pem"))

if __name__ == "__main__":
    import ipaddress
    cert_path, key_path = create_ssl_certificate()
    
    print("\n=== COMO USAR ===")
    print("Para iniciar o servidor Django com SSL:")
    print(f"python manage.py runserver_plus --cert-file {cert_path} --key-file {key_path} 127.0.0.1:8000")
    print("\nOu use o comando personalizado:")
    print("python manage.py runssl")