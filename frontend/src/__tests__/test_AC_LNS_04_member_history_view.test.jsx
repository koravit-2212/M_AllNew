import { render, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'

import LoanHistoryPage from '../pages/LoanHistoryPage.jsx'

describe('T-09 loan history page', () => {
  it('AC-LNS-04: shows the member history with return status and penalty information', async () => {
    const client = {
      getLoanHistory: vi.fn().mockResolvedValue({
        member_id: 'STD-1001',
        history: [
          {
            loan_id: 'loan-101',
            title: 'Clean Code',
            copy_id: 'CC-101',
            borrow_date: '2026-11-12',
            due_date: '2026-11-19',
            return_date: '2026-11-30',
            status: 'returned',
            penalty_amount: 12,
          },
          {
            loan_id: 'loan-102',
            title: 'Clean Architecture',
            copy_id: 'CC-102',
            borrow_date: '2026-12-01',
            due_date: '2026-12-08',
            return_date: null,
            status: 'borrowed',
            penalty_amount: 0,
          },
        ],
      }),
    }

    render(<LoanHistoryPage client={client} defaultMemberId="STD-1001" />)

    await waitFor(() => expect(client.getLoanHistory).toHaveBeenCalledWith({ memberId: 'STD-1001' }))

    expect(await screen.findByText('ประวัติการยืม-คืน')).toBeTruthy()
    expect(screen.getByText('Clean Code')).toBeTruthy()
    expect(screen.getByText('คืนแล้ว')).toBeTruthy()
    expect(screen.getByText('ยังไม่คืน')).toBeTruthy()
    expect(screen.getByText('ค่าปรับ 12 บาท')).toBeTruthy()
  })
})
