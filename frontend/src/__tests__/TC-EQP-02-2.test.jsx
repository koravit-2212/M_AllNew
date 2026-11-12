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

test('test_TC_EQP_02_2_staff_reviews_before_approve', async () => {
  // Given ปลั๊กไฟคงเหลือ 4 นักศึกษาไม่มีรายการค้างคืน
  const client = staffClient(pending(), LOAN_RESULT)

  // When นักศึกษาส่งคำขอยืม 1 ชิ้น แล้วเจ้าหน้าที่เปิดคำขอนั้น ยังไม่กดอนุมัติ
  await openRequest(client)

  // Then (3) เจ้าหน้าที่เห็นชื่อและรหัสนักศึกษา อุปกรณ์และจำนวน และไม่มีรายการค้างคืน
  // ((1)(2) สถานะคำขอและคงเหลือ ตรวจด้วย pytest)
  const card = within(screen.getByLabelText('ข้อมูลคำขอ'))
  expect(card.getByText('นักศึกษาทดสอบ (64000001)')).toBeTruthy()
  expect(card.getByText('ปลั๊กไฟ × 1')).toBeTruthy()
  expect(card.getByText('รายการค้างคืน')).toBeTruthy()
  expect(card.getByText('ไม่มี')).toBeTruthy()
  expect(client.approveLoanRequest).not.toHaveBeenCalled()
})
