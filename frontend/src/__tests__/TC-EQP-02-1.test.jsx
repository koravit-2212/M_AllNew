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

test('test_TC_EQP_02_1_approve_records_loan_and_reduces_stock', async () => {
  // Given ปลั๊กไฟคงเหลือ 4 นักศึกษาไม่มีรายการค้างคืน มีคำขอยืม 1 ชิ้นรออนุมัติ วันที่ยืม 2569-11-12
  const client = staffClient(pending(), LOAN_RESULT)
  await openRequest(client)

  // When เจ้าหน้าที่อนุมัติการยืม
  fireEvent.click(screen.getByRole('button', { name: 'อนุมัติการยืม' }))
  await waitFor(() => expect(client.approveLoanRequest).toHaveBeenCalledWith('REQ-0001'))

  // Then (5) หน้าจอเจ้าหน้าที่แสดงว่าบันทึกการยืมแล้ว พร้อมจำนวนคงเหลือใหม่และ due date
  // ((1)-(4) การบันทึก ตรวจด้วย pytest)
  expect(await screen.findByText('บันทึกการยืมแล้ว')).toBeTruthy()
  expect(screen.getByText(/คงเหลือ 3/)).toBeTruthy()
  expect(within(screen.getByLabelText('กำหนดคืนที่บันทึก')).getByText(/13 พ\.ย\. 2569/)).toBeTruthy()
})
