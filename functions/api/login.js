import bcrypt from 'bcryptjs';

export async function onRequestPost(context) {
  const { request, env } = context;
  const { usuario, senha } = await request.json();
  const usuarioNormalizado = String(usuario || '').trim().toLowerCase();

  if (!usuarioNormalizado || !senha) {
    return new Response(JSON.stringify({ message: "Informe usuário e senha." }), { status: 400 });
  }

  // Controle de Bloqueio (Rate Limit) via D1
  const ip = request.headers.get('CF-Connecting-IP') || 'local';
  const chaveLimit = `${ip}:${usuarioNormalizado}`;
  const agora = Math.floor(Date.now() / 1000);

  const registroLimit = await env.DB.prepare("SELECT * FROM rate_limit WHERE chave = ?").bind(chaveLimit).first();
  if (registroLimit && registroLimit.bloqueado_ate > agora) {
    const restante = registroLimit.bloqueado_ate - agora;
    return new Response(JSON.stringify({ message: `Muitas tentativas. Tente novamente em ${restante}s.` }), { status: 429 });
  }

  // Buscar usuário no banco D1
  const user = await env.DB.prepare("SELECT * FROM usuarios WHERE email = ?").bind(usuarioNormalizado).first();

  let senhaValida = false;
  if (user) {
    senhaValida = await bcrypt.compare(senha, user.senha_hash);
  }

  if (!user || !senhaValida) {
    const tentativas = registroLimit ? registroLimit.tentativas + 1 : 1;
    const bloqueadoAte = tentativas >= 5 ? agora + 120 : 0; 

    await env.DB.prepare(`
      INSERT INTO rate_limit (chave, tentativas, bloqueado_ate) 
      VALUES (?, ?, ?) 
      ON CONFLICT(chave) DO UPDATE SET tentativas = ?, bloqueado_ate = ?
    `).bind(chaveLimit, tentativas, bloqueadoAte, tentativas, bloqueadoAte).run();

    return new Response(JSON.stringify({ message: "Usuário ou senha incorretos." }), { status: 401 });
  }

  // Sucesso: Limpa erros e gera o Cookie de Sessão (8 horas)
  await env.DB.prepare("DELETE FROM rate_limit WHERE chave = ?").bind(chaveLimit).run();
  
  const sessaoDados = JSON.stringify({ usuario: usuarioNormalizado, exp: agora + (8 * 60 * 60) });
  const cookie = `gestao_fundiaria_session=${btoa(sessaoDados)}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=28800`;

  return new Response(JSON.stringify({ authenticated: true, usuario: usuarioNormalizado, message: "Acesso autorizado. Carregando mapa..." }), {
    status: 200,
    headers: { 'Set-Cookie': cookie, 'Content-Type': 'application/json' }
  });
}
