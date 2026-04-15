'use client'

import { useAnalysisStore } from '@/store/analysis'
import { useRouter } from 'next/navigation'
import { Clock, Search, Trash2, ArrowRight } from 'lucide-react'

export default function HistoryPage() {
    const { history, clearHistory, deleteHistoryItem, setParams, setResults } = useAnalysisStore()
    const router = useRouter()

    const handleReplay = (item: typeof history[0]) => {
        setParams(item.params)
        setResults(item.results)
        router.push('/results')
    }

    return (
        <div className="max-w-5xl mx-auto space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-text-primary tracking-tight">Historique d'analyses</h1>
                    <p className="text-sm text-text-muted mt-1">Consultez, comparez et reprenez vos rapports de marché précédents.</p>
                </div>
                {history.length > 0 && (
                    <button
                        onClick={clearHistory}
                        className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-danger-600 bg-danger-50 hover:bg-danger-100 rounded-md transition-colors"
                    >
                        <Trash2 className="w-4 h-4" />
                        Tout effacer
                    </button>
                )}
            </div>

            {history.length === 0 ? (
                <div className="bg-surface border border-border rounded-lg p-16 text-center space-y-4">
                    <div className="w-16 h-16 bg-background rounded-full flex items-center justify-center mx-auto">
                        <Clock className="w-8 h-8 text-text-muted" />
                    </div>
                    <div>
                        <h3 className="text-lg font-bold text-text-primary">Aucun historique</h3>
                        <p className="text-sm text-text-secondary mt-1">Vous n'avez pas encore effectué d'analyse de marché.</p>
                    </div>
                    <button
                        onClick={() => router.push('/analyze')}
                        className="mt-6 inline-flex items-center gap-2 px-6 py-2 bg-primary-600 text-white font-semibold rounded-md hover:bg-primary-700 transition-colors"
                    >
                        <Search className="w-4 h-4" /> Nouvelle analyse
                    </button>
                </div>
            ) : (
                <div className="bg-surface border border-border rounded-lg shadow-sm overflow-hidden">
                    <table className="w-full text-left text-sm whitespace-nowrap">
                        <thead className="bg-background text-xs text-text-muted font-semibold uppercase tracking-wider border-b border-border">
                            <tr>
                                <th className="px-6 py-4">Date</th>
                                <th className="px-6 py-4">Produit</th>
                                <th className="px-6 py-4">HS Code</th>
                                <th className="px-6 py-4">Périmètre</th>
                                <th className="px-6 py-4">Meilleur Score</th>
                                <th className="px-6 py-4 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                            {history.map((item) => (
                                <tr key={item.id} className="hover:bg-background/50 transition-colors group">
                                    <td className="px-6 py-4 text-text-secondary font-medium">
                                        {new Date(item.date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}
                                    </td>
                                    <td className="px-6 py-4 font-bold text-text-primary">{item.params.product_name}</td>
                                    <td className="px-6 py-4 font-mono text-text-muted">{item.params.hs_code}</td>
                                    <td className="px-6 py-4 text-text-secondary">Top {item.params.top_n === 50 ? 'Général' : item.params.top_n}</td>
                                    <td className="px-6 py-4">
                                        <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-bold ${item.topScore >= 80 ? 'bg-success/10 text-success' : item.topScore >= 60 ? 'bg-warning-100 text-warning-600' : 'bg-danger-50 text-danger-600'
                                            }`}>
                                            {item.topScore}%
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-right flex items-center justify-end gap-2">
                                        <button
                                            onClick={() => handleReplay(item)}
                                            className="px-3 py-1.5 text-xs font-bold text-primary-600 bg-primary-50 rounded hover:bg-primary-100 transition-colors flex items-center gap-1 opacity-100 lg:opacity-0 lg:group-hover:opacity-100"
                                        >
                                            Voir rapport <ArrowRight className="w-3 h-3" />
                                        </button>
                                        <button
                                            onClick={() => deleteHistoryItem(item.id)}
                                            className="p-1.5 text-text-muted hover:text-danger-600 rounded transition-colors opacity-100 lg:opacity-0 lg:group-hover:opacity-100"
                                            title="Supprimer"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    )
}
