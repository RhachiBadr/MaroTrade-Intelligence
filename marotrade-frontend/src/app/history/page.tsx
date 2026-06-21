'use client'

import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import { ArrowRight, Clock, Search, Trash2 } from 'lucide-react'
import { useAnalysisStore, type HistoryItem } from '@/store/analysis'
import { deleteWorkspaceAnalysis, fetchWorkspaceAnalyses, type WorkspaceAnalysis } from '@/lib/auth-api'
import { PageContainer, PageHeader } from '@/components/ui/page-shell'
import { useI18n } from '@/lib/i18n'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/components/auth/AuthProvider'

type DisplayAnalysis = {
  id: string
  product_name: string
  hs_code: string
  top_n: number
  results: WorkspaceAnalysis['results']
  created_at: string
  source: 'server' | 'local'
}

function fromWorkspaceAnalysis(item: WorkspaceAnalysis): DisplayAnalysis {
  return {
    id: item.id,
    product_name: item.product_name,
    hs_code: item.hs_code,
    top_n: item.top_n,
    results: item.results,
    created_at: item.created_at,
    source: 'server',
  }
}

function fromLocalHistory(item: HistoryItem): DisplayAnalysis {
  return {
    id: item.id,
    product_name: item.params.product_name,
    hs_code: item.params.hs_code,
    top_n: item.params.top_n,
    results: item.results,
    created_at: item.date,
    source: 'local',
  }
}

export default function HistoryPage() {
  const { t } = useI18n()
  const { account } = useAuth()
  const router = useRouter()
  const queryClient = useQueryClient()
  const {
    setParams,
    setResults,
    history: localHistory,
    deleteHistoryItem,
  } = useAnalysisStore()

  const {
    data: serverHistory = [],
    isLoading,
    isError,
  } = useQuery({
    queryKey: ['workspace-analyses'],
    queryFn: fetchWorkspaceAnalyses,
    retry: false,
  })

  const history: DisplayAnalysis[] =
    serverHistory.length > 0
      ? serverHistory.map(fromWorkspaceAnalysis)
      : localHistory.map(fromLocalHistory)
  const usingLocalHistory = serverHistory.length === 0 && localHistory.length > 0
  const organizationName = account?.organization.name?.trim()
  const pageTitle = organizationName
    ? `Historique de votre ${organizationName}`
    : t('pages.historyTitle')

  function handleReplay(item: DisplayAnalysis) {
    setParams({ product_name: item.product_name, hs_code: item.hs_code, top_n: item.top_n })
    setResults(item.results)
    router.push('/results')
  }

  async function handleDelete(item: DisplayAnalysis) {
    if (item.source === 'local') {
      deleteHistoryItem(item.id)
      return
    }

    await deleteWorkspaceAnalysis(item.id)
    await queryClient.invalidateQueries({ queryKey: ['workspace-analyses'] })
  }

  return (
    <PageContainer className="max-w-5xl space-y-6 py-2">
      <PageHeader
        title={pageTitle}
        description={t('pages.historySubtitle')}
      />

      {(isError || usingLocalHistory) && (
        <div className="rounded-lg border border-warning-500/20 bg-warning-50 px-4 py-3 text-sm font-medium text-warning-700 dark:bg-warning-950/25 dark:text-warning-200">
          Historique local affiche : les analyses sont conservees dans ce navigateur. Connectez PostgreSQL pour l'historique securise par compte PME.
        </div>
      )}

      {isLoading && history.length === 0 ? (
        <Card className="py-16 text-center shadow-none">
          <Clock className="mx-auto h-8 w-8 animate-pulse text-primary-600" />
          <p className="mt-3 text-sm text-text-secondary">Chargement de vos analyses...</p>
        </Card>
      ) : history.length === 0 ? (
        <Card className="py-16 text-center shadow-none">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-secondary">
            <Clock className="h-8 w-8 text-text-muted" />
          </div>
          <h3 className="text-lg font-semibold text-text-primary">Aucune analyse enregistree</h3>
          <p className="mx-auto mt-1 max-w-md text-sm text-text-secondary">
            Lancez une analyse pour creer le premier rapport partage avec votre equipe.
          </p>
          <Button type="button" className="mt-6 gap-2" onClick={() => router.push('/analyze')}>
            <Search className="h-4 w-4" />
            Nouvelle analyse
          </Button>
        </Card>
      ) : (
        <Card className="overflow-hidden shadow-none">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[720px] text-left text-sm">
              <thead className="border-b border-border bg-secondary/50 text-xs font-medium uppercase tracking-wide text-text-muted">
                <tr>
                  <th className="px-4 py-3 sm:px-6">Date</th>
                  <th className="px-4 py-3 sm:px-6">Produit</th>
                  <th className="px-4 py-3 sm:px-6">HS</th>
                  <th className="px-4 py-3 sm:px-6">Perimetre</th>
                  <th className="px-4 py-3 sm:px-6">Meilleur score</th>
                  <th className="px-4 py-3 sm:px-6">Stockage</th>
                  <th className="px-4 py-3 text-right sm:px-6">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {history.map((item) => {
                  const topScore = item.results[0]?.score_final ?? 0
                  return (
                    <tr key={item.id} className="group hover:bg-secondary/40">
                      <td className="px-4 py-3.5 text-text-secondary sm:px-6">
                        {new Intl.DateTimeFormat('fr-FR', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(item.created_at))}
                      </td>
                      <td className="px-4 py-3.5 font-medium text-text-primary sm:px-6">{item.product_name}</td>
                      <td className="px-4 py-3.5 font-mono text-text-muted sm:px-6">{item.hs_code}</td>
                      <td className="px-4 py-3.5 text-text-secondary sm:px-6">Top {item.top_n}</td>
                      <td className="px-4 py-3.5 sm:px-6">
                        <span className="inline-flex rounded-full bg-success-muted px-2.5 py-0.5 text-xs font-semibold text-success">
                          {Math.round(topScore)}%
                        </span>
                      </td>
                      <td className="px-4 py-3.5 sm:px-6">
                        <span className="inline-flex rounded-full bg-secondary px-2.5 py-0.5 text-xs font-semibold text-text-secondary">
                          {item.source === 'server' ? 'Compte PME' : 'Navigateur'}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 text-right sm:px-6">
                        <div className="flex items-center justify-end gap-2">
                          <Button type="button" variant="ghost" size="sm" onClick={() => handleReplay(item)} className="gap-1">
                            Voir <ArrowRight className="h-3 w-3" />
                          </Button>
                          <button
                            type="button"
                            onClick={() => void handleDelete(item)}
                            className="rounded-md p-2 text-text-muted transition-colors hover:bg-danger-50 hover:text-danger-600"
                            title="Supprimer"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </PageContainer>
  )
}
