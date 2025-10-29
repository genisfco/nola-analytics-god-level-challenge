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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-2xl mx-auto text-center">
          <h1 className="text-5xl font-bold text-slate-900 mb-4">
            🍔 Restaurant Analytics
          </h1>
          <p className="text-xl text-slate-600 mb-8">
            Plataforma de analytics customizável para restaurantes
          </p>
          
          <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
            <h2 className="text-2xl font-semibold text-slate-800 mb-4">
              Status do Sistema
            </h2>
            
            {isLoading && (
              <div className="text-slate-600">Carregando...</div>
            )}
            
            {error && (
              <div className="text-red-600">
                ❌ Erro ao conectar com o backend
                <p className="text-sm mt-2">
                  Certifique-se que o backend está rodando em http://localhost:8000
                </p>
              </div>
            )}
            
            {data && (
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-green-50 rounded">
                  <span className="font-medium text-slate-700">Status API</span>
                  <span className="text-green-600 font-semibold">
                    ✅ {data.status}
                  </span>
                </div>
                <div className="flex items-center justify-between p-3 bg-blue-50 rounded">
                  <span className="font-medium text-slate-700">Database</span>
                  <span className="text-blue-600 font-semibold">
                    {data.database === 'connected' ? '✅' : '❌'} {data.database}
                  </span>
                </div>
                <div className="flex items-center justify-between p-3 bg-purple-50 rounded">
                  <span className="font-medium text-slate-700">Cache</span>
                  <span className="text-purple-600 font-semibold">
                    {data.cache === 'connected' ? '✅' : '❌'} {data.cache}
                  </span>
                </div>
              </div>
            )}
          </div>

          <div className="text-sm text-slate-500">
            <p>Nola God Level Challenge • 2025</p>
            <p className="mt-2">
              Documentação da API: {' '}
              <a 
                href="http://localhost:8000/docs" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 underline"
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

