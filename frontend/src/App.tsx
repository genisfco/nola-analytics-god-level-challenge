import { useQuery } from '@tanstack/react-query'

function App() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const response = await fetch('http://localhost:8000/health')
      if (!response.ok) throw new Error('Failed to fetch')
      return response.json()
    },
  })

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-2xl mx-auto text-center">
          <h1 className="text-5xl font-bold text-foreground mb-4">
            🍔 Restaurant Analytics
          </h1>
          <p className="text-xl text-muted-foreground mb-8">
            Plataforma de analytics customizável para restaurantes
          </p>
          
          <div className="bg-card rounded-lg shadow-lg border border-border p-8 mb-8">
            <h2 className="text-2xl font-semibold text-card-foreground mb-4">
              Status do Sistema
            </h2>
            
            {isLoading && (
              <div className="text-muted-foreground">Carregando...</div>
            )}
            
            {error && (
              <div className="text-destructive bg-destructive/10 p-4 rounded-lg">
                ❌ Erro ao conectar com o backend
                <p className="text-sm mt-2">
                  Certifique-se que o backend está rodando em http://localhost:8000
                </p>
              </div>
            )}
            
            {data && (
              <div className="space-y-3">
                <div className="flex items-center justify-between p-4 bg-primary/5 border-l-4 border-primary rounded-lg">
                  <span className="font-medium text-card-foreground">Status API</span>
                  <span className="text-primary font-semibold">
                    ✅ {data.status}
                  </span>
                </div>
                <div className="flex items-center justify-between p-4 bg-secondary/5 border-l-4 border-secondary rounded-lg">
                  <span className="font-medium text-card-foreground">Database</span>
                  <span className="text-secondary font-semibold">
                    {data.database === 'connected' ? '✅' : '❌'} {data.database}
                  </span>
                </div>
                <div className="flex items-center justify-between p-4 bg-primary/5 border-l-4 border-primary rounded-lg">
                  <span className="font-medium text-card-foreground">Cache</span>
                  <span className="text-primary font-semibold">
                    {data.cache === 'connected' ? '✅' : '❌'} {data.cache}
                  </span>
                </div>
              </div>
            )}
          </div>

          <div className="text-sm text-muted-foreground">
            <p className="font-medium">Nola God Level Challenge • 2025</p>
            <p className="mt-2">
              Documentação da API: {' '}
              <a 
                href="http://localhost:8000/docs" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-primary hover:text-secondary underline transition-colors"
              >
                /docs
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App

