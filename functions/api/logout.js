export async function onRequestPost() {
  const cookie = `gestao_fundiaria_session=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0; Expires=Thu, 01 Jan 1970 00:00:00 GMT`;
  return new Response(JSON.stringify({ authenticated: false, message: "Sessão encerrada." }), {
    status: 200,
    headers: { 'Set-Cookie': cookie, 'Content-Type': 'application/json' }
  });
}
