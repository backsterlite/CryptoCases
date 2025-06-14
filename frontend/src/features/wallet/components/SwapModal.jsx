import React, { useState, useEffect, useCallback, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { 
  fetchSwapQuote, 
  swapCoins, 
  fetchWallets, 
  clearSwapQuote, 
  clearSwapErrors,
  resetSwapStatus 
} from '../walletSlice'
import BalanceSelector from './BalanceSelector'
import './css/SwapModal.css'

const SwapModal = ({ isOpen, onClose }) => {
  const dispatch = useDispatch()

  // Redux state
  const wallets = useSelector((state) => state.wallet.wallets)
  const swapQuote = useSelector((state) => state.wallet.swapQuote.data)
  const quoteLoading = useSelector((state) => state.wallet.swapQuote.loading)
  const quoteError = useSelector((state) => state.wallet.swapQuote.error)
  const swapLoading = useSelector((state) => state.wallet.swapStatus.loading)
  const swapError = useSelector((state) => state.wallet.swapStatus.error)
  const swapSuccess = useSelector((state) => state.wallet.swapStatus.success)

  // Local state
  const [from, setFrom] = useState({ symbol: '', network: null })
  const [to, setTo] = useState({ symbol: '', network: null })
  const [amountToSell, setAmountToSell] = useState('')
  const [debouncedAmount, setDebouncedAmount] = useState('')
  
  // Refs для debounce
  const debounceTimer = useRef(null)

  // Очищення при закритті модалки
  useEffect(() => {
    if (!isOpen) {
      // Очищаємо все при закритті
      setFrom({ symbol: '', network: null })
      setTo({ symbol: '', network: null })
      setAmountToSell('')
      setDebouncedAmount('')
      dispatch(clearSwapQuote())
      dispatch(clearSwapErrors())
      dispatch(resetSwapStatus())
    }
  }, [isOpen, dispatch])

  // Debounce для суми
  useEffect(() => {
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current)
    }

    debounceTimer.current = setTimeout(() => {
      setDebouncedAmount(amountToSell)
    }, 500) // 500ms затримка

    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current)
      }
    }
  }, [amountToSell])

  // Очищення quote при зміні токенів
  useEffect(() => {
    dispatch(clearSwapQuote())
    dispatch(clearSwapErrors())
    setAmountToSell('')
    setDebouncedAmount('')
  }, [from.symbol, from.network, to.symbol, to.network, dispatch])

  // Запит quote при зміні параметрів
  useEffect(() => {
    if (
      !from.symbol ||
      !to.symbol ||
      !debouncedAmount ||
      parseFloat(debouncedAmount) <= 0 ||
      from.symbol === to.symbol
    ) {
      return
    }

    dispatch(
      fetchSwapQuote({
        fromToken: from.symbol,
        toToken: to.symbol,
        amount: debouncedAmount,
        fromNetwork: from.network,
        toNetwork: to.network
      })
    )
  }, [from, to, debouncedAmount, dispatch])

  // Успішний swap
  useEffect(() => {
    if (swapSuccess) {
      console.log("fetch wallet Modal page")
      dispatch(fetchWallets())
      dispatch(resetSwapStatus())
      setTimeout(() => {
        onClose()
      }, 1000)
    }
  }, [swapSuccess, dispatch, onClose])

  // Нормалізація network для порівняння
  const normalizeNetwork = (network) => {
    if (network === null || network === 'None' || network === 'null') {
      return 'None'
    }
    return network
  }

  // Обчислення балансу
  const getBalance = useCallback(() => {
    if (!from.symbol || !wallets[from.symbol]) return 0
    
    const normalizedNetwork = normalizeNetwork(from.network)
    const balance = wallets[from.symbol].balance[normalizedNetwork]
    
    return balance ? parseFloat(balance) : 0
  }, [from, wallets])

  const fromBalance = getBalance()

  // Валідація
  const isValidAmount = amountToSell && 
    parseFloat(amountToSell) > 0 && 
    parseFloat(amountToSell) <= fromBalance

  const canSwap = from.symbol &&
    to.symbol &&
    from.symbol !== to.symbol &&
    isValidAmount &&
    swapQuote &&
    !quoteLoading &&
    !swapLoading

  const handleSwap = () => {
    if (!canSwap) return
    
    dispatch(
      swapCoins({
        fromToken: from.symbol,
        toToken: to.symbol,
        amount: amountToSell,
        fromNetwork: from.network,
        toNetwork: to.network
      })
    )
  }

  const handleSelectChange = useCallback((newFrom, newTo) => {
    setFrom(newFrom)
    setTo(newTo)
  }, [])

  const handleAmountChange = (e) => {
    const value = e.target.value
    // Дозволяємо тільки числа з крапкою
    if (value === '' || /^\d*\.?\d*$/.test(value)) {
      setAmountToSell(value)
    }
  }

  const handleMaxClick = () => {
    setAmountToSell(fromBalance.toString())
  }

  if (!isOpen) return null

  return (
    <div className="modal-backdrop">
      <div className="modal">
        <div className="modal-header">
          <h3>Swap Tokens</h3>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <BalanceSelector onChange={handleSelectChange} />

        <div className="amount-section">
          <label>Amount to sell:</label>
          <div className="amount-input-wrapper">
            <input
              type="text"
              value={amountToSell}
              onChange={handleAmountChange}
              placeholder="0.00"
              className={!isValidAmount && amountToSell ? 'error' : ''}
            />
            <button 
              className="max-btn" 
              onClick={handleMaxClick}
              disabled={!from.symbol || fromBalance === 0}
            >
              MAX
            </button>
          </div>
          <div className="balance-info">
            Balance: {fromBalance.toFixed(6)} {from.symbol || ''}
          </div>
          {!isValidAmount && amountToSell && (
            <div className="error-message">Insufficient balance</div>
          )}
        </div>

        <div className="receive-section">
          <label>Estimated receive:</label>
          {quoteLoading ? (
            <div className="loading">Calculating...</div>
          ) : quoteError ? (
            <div className="error-message">Error: {quoteError}</div>
          ) : swapQuote ? (
            <div className="quote-result">
              {swapQuote.to_amount} {to.symbol}
            </div>
          ) : (
            <div className="quote-placeholder">Enter amount to see estimate</div>
          )}
        </div>

        {swapError && (
          <div className="error-message swap-error">
            Swap failed: {swapError}
          </div>
        )}

        {swapSuccess && (
          <div className="success-message">
            Swap successful! Updating balances...
          </div>
        )}

        <div className="modal-actions">
          <button 
            className="swap-btn" 
            onClick={handleSwap} 
            disabled={!canSwap}
          >
            {swapLoading ? 'Swapping…' : 'Swap'}
          </button>
          <button className="cancel-btn" onClick={onClose}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}

export default SwapModal