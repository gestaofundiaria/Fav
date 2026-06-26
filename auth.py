import os
import time
import bcrypt
import logging
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ─── Carregamento de usuários ─────────────────────────────────
def _carregar_usuarios() -> dict:
    """
    Lê credenciais das variáveis de ambiente.
    Formato esperado: USER_1_NAME / USER_1_HASH, USER_2_NAME / USER_2_HASH, ...
    """
    usuarios = {}
    i = 1
    while True:
        nome = os.environ.get(f'USER_{i}_NAME')
        hash_ = os.environ.get(f'USER_{i}_HASH')
        if not nome or not hash_:
            break
        usuarios[nome.strip().lower()] = hash_.strip()
        i += 1

    if not usuarios:
        logger.critical('Nenhum usuário encontrado nas variáveis de ambiente. '
                        'Configure USER_1_NAME e USER_1_HASH.')
    else:
        logger.info('✓ %d usuário(s) carregado(s) das variáveis de ambiente.', len(usuarios))

    return usuarios


USUARIOS = _carregar_usuarios()


# ─── Rate limiting por IP ─────────────────────────────────────
_tentativas: dict = defaultdict(list)

MAX_TENTATIVAS      = 5    # tentativas permitidas na janela
JANELA_SEGUNDOS     = 300  # janela de 5 minutos
BLOQUEIO_SEGUNDOS   = 900  # bloqueio de 15 minutos após exceder


def _checar_rate_limit(ip: str) -> None:
    """Lança RuntimeError se o IP excedeu o limite de tentativas."""
    agora = time.time()
    _tentativas[ip] = [t for t in _tentativas[ip] if agora - t < JANELA_SEGUNDOS]

    if len(_tentativas[ip]) >= MAX_TENTATIVAS:
        tempo_restante = int(BLOQUEIO_SEGUNDOS - (agora - _tentativas[ip][0]))
        logger.warning('Rate limit atingido para IP: %s', ip)
        raise RuntimeError(f'Muitas tentativas. Tente novamente em {tempo_restante} segundos.')


def _registrar_tentativa(ip: str) -> None:
    """Registra uma tentativa de login falha."""
    _tentativas[ip].append(time.time())
    restantes = max(0, MAX_TENTATIVAS - len(_tentativas[ip]))
    logger.warning('Tentativa falha para IP: %s — %d restante(s).', ip, restantes)


def _limpar_tentativas(ip: str) -> None:
    """Remove o histórico de tentativas após login bem-sucedido."""
    _tentativas.pop(ip, None)


# ─── Autenticação ─────────────────────────────────────────────
def get_user(login: str) -> dict | None:
    """Retorna o usuário pelo login, ou None se não encontrado."""
    login = login.strip().lower()
    hash_ = USUARIOS.get(login)
    if not hash_:
        logger.debug('Usuário não encontrado: %s', login)
        return None
    return {'login': login, 'hash': hash_}


def verify_password(stored_hash: str, password: str) -> bool:
    """Verifica se a senha corresponde ao hash bcrypt armazenado."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
    except Exception:
        logger.warning('Erro ao verificar hash bcrypt.')
        return False


def autenticar(login: str, senha: str, ip: str) -> dict:
    """
    Autentica um usuário com rate limiting por IP.
    Retorna o dicionário do usuário ou lança RuntimeError.
    """
    _checar_rate_limit(ip)

    usuario = get_user(login)
    if not usuario or not verify_password(usuario['hash'], senha):
        _registrar_tentativa(ip)
        raise RuntimeError('Usuário ou senha incorretos.')

    _limpar_tentativas(ip)
    logger.info(
    'Login bem-sucedido para usuário autorizado (%s)',
    ip
    )
    return usuario


def init_db() -> bool:
    """
    Mantido por compatibilidade com app.py.
    Valida que ao menos um usuário foi carregado das variáveis de ambiente.
    """
    if not USUARIOS:
        raise RuntimeError('Nenhum usuário configurado. Defina USER_1_NAME e USER_1_HASH.')
    logger.info('✓ Autenticação inicializada com %d usuário(s).', len(USUARIOS))
    return True