import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { vi } from 'vitest'

import StaffLoanApprovalPage from '../pages/StaffLoanApprovalPage.jsx'

// test จาก specs/007-equipment/test-cases.md ห้ามแก้ให้ผ่าน
function pending(overrides = {}) {
  return {
    request_id: 'REQ-0001',
    status: 'pending',
    quantity: 1,
    student: { student_id: '64000001', name: 'นักศึกษาทดสอบ' },
    has_outstanding: false,
    blocked: false,
    outstanding_items: [],
    equipment: { equipment_type_id: 'EQ-PLUG', name: 'ปลั๊กไฟ', available_count: 4 },
    due_date: '2026-11-13',
    ...overrides,
  }
}

function staffClient(request, loanResult) {
  return {
    listPendingLoanRequests: vi.fn().mockResolvedValueOnce({ items: [request] }).mockResolvedValue({ items: [] }),
    approveLoanRequest: vi.fn().mockResolvedValue(loanResult),
    overrideLoanRequest: vi.fn().mockResolvedValue({ ...loanResult, override: true }),
  }
}

const LOAN_RESULT = {
  loan_id: 'LOAN-0001',
  request_id: 'REQ-0001',
  equipment_name: 'ปลั๊กไฟ',
  quantity: 1,
  available_count: 3,
  due_date: '2026-11-13',
}

async function openRequest(client) {
  render(<StaffLoanApprovalPage client={client} />)
  fireEvent.click(await screen.findByRole('button', { name: /นักศึกษาทดสอบ/ }))
}

test('test_TC_EQP_04_2_override_records_loan', async () => {
  // Given เหมือน TC-EQP-04-1 และเจ้าหน้าที่ตรวจรายการค้างคืนแล้ว
  const request = pending({ has_outstanding: true, blocked: true, outstanding_items: [{ item: 'ร่ม', days_overdue: 2 }] })
  const client = staffClient(request, LOAN_RESULT)
  await openRequest(client)

  // When เจ้าหน้าที่กดปลดล็อก (override) โดยไม่ใส่เหตุผล
  fireEvent.click(screen.getByRole('button', { name: /override/ }))

  // Then (1) override สำเร็จโดยไม่ต้องใส่เหตุผล (ไม่มีช่องให้กรอก)
  await waitFor(() => expect(client.overrideLoanRequest).toHaveBeenCalledWith('REQ-0001'))
  expect(screen.queryByRole('textbox')).toBeNull()
  // (4) หน้าจอเจ้าหน้าที่แสดงว่าบันทึกการยืมแล้ว
  expect(await screen.findByText('บันทึกการยืมแล้ว')).toBeTruthy()
  // ((2)(3) การบันทึก due date และคงเหลือ ตรวจด้วย pytest)
})
