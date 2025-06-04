import React, { useEffect, useState, useMemo } from 'react'
import { useSelector } from 'react-redux'

export default function BalanceSelector({ onChange }) {
  const wallets = useSelector((s) => s.wallet.wallets)
  const loading = useSelector((s) => s.wallet.walletsLoading)

  const [fromKey, setFromKey] = useState('')
  const [toKey, setToKey] = useState('')

  // Нормалізація network для консистентності
  const normalizeNetwork = (network) => {
    if (network === null || network === 'None' || network === 'null') {
      return 'None'
    }
    return network
  }

  // Створюємо опції з нормалізованими мережами
  const options = useMemo(() => {
    if (!wallets || Object.keys(wallets).length === 0) return []

    return Object.entries(wallets).flatMap(([symbol, wallet]) =>
      Object.entries(wallet.balance).map(([network, amount]) => {
        const normalizedNetwork = normalizeNetwork(network)
        return {
          key: `${symbol}|${normalizedNetwork}`,
          label: `${symbol} (${normalizedNetwork === 'None' ? 'Default' : normalizedNetwork}) - Balance: ${amount}`,
          symbol: symbol,
          network: network === 'None' ? null : network,
          amount: amount
        }
      })
    )
  }, [wallets])

  // Фільтровані опції для "To"
  const filteredToOptions = useMemo(() => {
    if (!fromKey) return options
    const [fromSymbol] = fromKey.split('|')
    return options.filter((o) => o.symbol !== fromSymbol)
  }, [options, fromKey])

  // Парсинг ключа
  const parseKey = (key) => {
    if (!key) return { symbol: '', network: null }
    const [symbol, network] = key.split('|')
    return { 
      symbol: symbol || '', 
      network: network === 'None' ? null : network 
    }
  }

  // Викликаємо onChange при зміні вибору
  useEffect(() => {
    const fromParsed = parseKey(fromKey)
    const toParsed = parseKey(toKey)
    onChange(fromParsed, toParsed)
  }, [fromKey, toKey, onChange])

  if (loading) return <div className="loading">Loading balances…</div>

  return (
    <div className="balance-selector">
      <div className="selector-row">
        <label>From:</label>
        <select 
          value={fromKey} 
          onChange={(e) => {
            setFromKey(e.target.value)
            // Якщо вибрали той самий токен що і в "To", очищаємо "To"
            const [newFromSymbol] = e.target.value.split('|')
            const [currentToSymbol] = toKey.split('|')
            if (newFromSymbol === currentToSymbol) {
              setToKey('')
            }
          }}
          className="token-select"
        >
          <option value="">Select token</option>
          {options.map((o) => (
            <option key={o.key} value={o.key}>
              {o.label}
            </option>
          ))}
        </select>
      </div>

      <div className="selector-row">
        <label>To:</label>
        <select 
          value={toKey} 
          onChange={(e) => setToKey(e.target.value)}
          className="token-select"
        >
          <option value="">Select token</option>
          {filteredToOptions.map((o) => (
            <option key={o.key} value={o.key}>
              {o.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  )
}