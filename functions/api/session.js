export async function onRequestGet(context) {
  const { request } = context;
  const cookieHeader = request.headers.get('Cookie') || '';
  const match = cookieHeader.match(/gestao_fundiaria_session=([^;]+)/);
  
  if (!match) return new Response(JSON.stringify({ authenticated: false }), { status: 200 });

  try {
    const dadosSessao = JSON.parse(atob(match[1]));
    const agora = Math.floor(Date.now() / 1000);

    if (dadosSessao.exp < agora) return new Response(JSON.stringify({ authenticated: false }), { status: 200 });

    return new Response(JSON.stringify({ authenticated: true, usuario: dadosSessao.usuario }), { status: 200 });
  } catch (e) {
    return new Response(JSON.stringify({ authenticated: false }), { status: 200 });
  }
}
