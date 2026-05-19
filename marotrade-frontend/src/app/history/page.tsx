'use client'

import { useAnalysisStore } from '@/store/analysis'
import { useRouter } from 'next/navigation'
import { Clock, Search, Trash2, ArrowRight } from 'lucide-react'
import { PageContainer, PageHeader } from '@/components/ui/page-shell'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

export default function HistoryPage() {
  const { history, clearHistory, deleteHistoryItem, setParams, setResults } = useAnalysisStore()
  const router = useRouter()

  function handleReplay(item: (typeof history)[0]) {
    setParams(item.params)
    setResults(item.results)
    router.push('/results')
  }

  return (
    <PageContainer className="max-w-5xl space-y-6 py-2">
      <PageHeader
        title="Historique des analyses"
        description="Consultez et rouvrez vos rapports de marché enregistrés sur cet appareil."
        actions={
          history.length > 0 ? (
            <Button type="button" variant="destructive" size="sm" onClick={clearHistory} className="gap-2">
              <Trash2 className="h-4 w-4" />
              Tout effacer
            </Button>
          ) : null
        }
      />

      {history.length === 0 ? (
        <Card className="py-16 text-center shadow-none">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-secondary">
            <Clock className="h-8 w-8 text-text-muted" />
          </div>
          <h3 className="text-lg font-semibold text-text-primary">Aucun historique</h3>
          <p className="mx-auto mt-1 max-w-md text-sm text-text-secondary">
            Vous n&apos;avez pas encore effectué d&apos;analyse de marché.
          </p>
          <Button type="button" className="mt-6 gap-2" onClick={() => router.push('/analyze')}>
            <Search className="h-4 w-4" />
            Nouvelle analyse
          </Button>
        </Card>
      ) : (
        <Card className="overflow-hidden shadow-none">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[640px] text-left text-sm">
              <thead className="border-b border-border bg-secondary/50 text-xs font-medium uppercase tracking-wide text-text-muted">
                <tr>
                  <th className="px-4 py-3 sm:px-6">Date</th>
                  <th className="px-4 py-3 sm:px-6">Produit</th>
                  <th className="px-4 py-3 sm:px-6">HS</th>
                  <th className="px-4 py-3 sm:px-6">Périmètre</th>
                  <th className="px-4 py-3 sm:px-6">Meilleur score</th>
                  <th className="px-4 py-3 text-right sm:px-6">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {history.map((item) => (
                  <tr key={item.id} className="group hover:bg-secondary/40">
                    <td className="px-4 py-3.5 text-text-secondary sm:px-6">
                      {new Date(item.date).toLocaleDateString('fr-FR', {
                        day: 'numeric',
                        month: 'short',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </td>
                    <td className="px-4 py-3.5 font-medium text-text-primary sm:px-6">
                      {item.params.product_name}
                    </td>
                    <td className="px-4 py-3.5 font-mono text-text-muted sm:px-6">{item.params.hs_code}</td>
                    <td className="px-4 py-3.5 text-text-secondary sm:px-6">
                      Top {item.params.top_n === 50 ? 'général' : item.params.top_n}
                    </td>
                    <td className="px-4 py-3.5 sm:px-6">
                      <span
                        className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                          item.topScore >= 80
                            ? 'bg-success-muted text-success'
                            : item.topScore >= 60
                              ? 'bg-warning-50 text-warning-600'
                              : 'bg-danger-50 text-danger-600'
                        }`}
                      >
                        {item.topScore}%
                      </span>
                    </td>
                    <td className="px-4 py-3.5 text-right sm:px-6">
                      <div className="flex items-center justify-end gap-2">
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => handleReplay(item)}
                          className="gap-1 opacity-100 lg:opacity-0 lg:group-hover:opacity-100"
                        >
                          Voir <ArrowRight className="h-3 w-3" />
                        </Button>
                        <button
                          type="button"
                          onClick={() => deleteHistoryItem(item.id)}
                          className="rounded-md p-2 text-text-muted transition-colors hover:bg-danger-50 hover:text-danger-600"
                          title="Supprimer"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </PageContainer>
  )
}
