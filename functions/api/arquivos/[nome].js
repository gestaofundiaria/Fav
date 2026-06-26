export async function onRequestGet(context) {
  const { request, env, params } = context;
  const nomeArquivo = params.nome; 

  // 1. Validar se o usuário está logado
  const cookieHeader = request.headers.get('Cookie') || '';
  const match = cookieHeader.match(/gestao_fundiaria_session=([^;]+)/);
  
  if (!match) {
    return new Response(JSON.stringify({ message: "Faça login para acessar este recurso." }), { status: 401 });
  }

  try {
    const dadosSessao = JSON.parse(atob(match[1]));
    if (dadosSessao.exp < Math.floor(Date.now() / 1000)) {
      return new Response(JSON.stringify({ message: "Sessão expirada. Faça login novamente." }), { status: 401 });
    }

    // 2. Puxar o arquivo do R2 'arquivos' usando o binding BUCKET
    const objeto = await env.BUCKET.get(nomeArquivo);
    if (!objeto) {
      return new Response(JSON.stringify({ message: "Arquivo não encontrado." }), { status: 404 });
    }

    // 3. Mapear o tipo do arquivo
    let contentType = 'application/octet-stream';
    if (nomeArquivo.endsWith('.geojson')) contentType = 'application/json';

    const headers = new Headers();
    objeto.writeHttpMetadata(headers);
    headers.set('Content-Type', contentType);
    headers.set('Cache-Control', 'no-store'); 

    return new Response(objeto.body, { status: 200, headers: headers });
  } catch (e) {
    return new Response(JSON.stringify({ message: "Erro interno no servidor." }), { status: 500 });
  }
}
