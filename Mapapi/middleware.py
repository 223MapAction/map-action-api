from django.urls import resolve, Resolver404


class SlashInsensitiveMiddleware:
    """Rend chaque route insensible au slash final.

    Les routes de /MapApi/ sont historiquement incohérentes : certaines finissent
    par « / », d'autres non. Le frontend renvoyait des 404 uniquement à cause d'un
    slash en trop ou en moins. Plutôt que d'éditer ~150 routes (et casser les
    appels existants), on retente de façon transparente la variante avec/sans slash
    AVANT le routage — même méthode HTTP, même corps de requête, sans redirection
    (contrairement à APPEND_SLASH qui redirige en 301 et casse les POST).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info
        if not self._resolves(path):
            toggled = path[:-1] if (path.endswith('/') and len(path) > 1) else path + '/'
            if self._resolves(toggled):
                request.path = request.path[:-1] if request.path.endswith('/') and len(request.path) > 1 else request.path + '/'
                request.path_info = toggled
        return self.get_response(request)

    @staticmethod
    def _resolves(path):
        try:
            resolve(path)
            return True
        except Resolver404:
            return False
