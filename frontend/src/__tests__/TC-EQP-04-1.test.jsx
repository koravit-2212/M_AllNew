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

test('test_TC_EQP_04_1_outstanding_shown_and_blocked', async () => {
  // Given นักศึกษาค้างคืนร่ม เกินกำหนด 2 วัน และปลั๊กไฟคงเหลือ 4
  const request = pending({ has_outstanding: true, blocked: true, outstanding_items: [{ item: 'ร่ม', days_overdue: 2 }] })
  const client = staffClient(request, LOAN_RESULT)

  // When นักศึกษาขอยืมปลั๊กไฟ 1 ชิ้น แล้วเจ้าหน้าที่เปิดคำขอ
  await openRequest(client)

  // Then (3) หน้าจอแสดงคำเตือนว่ามีรายการค้างคืน พร้อมรายการที่ค้าง
  const alert = within(screen.getByRole('alert'))
  expect(alert.getByText('มีรายการค้างคืน')).toBeTruthy()
  expect(alert.getByText(/ร่ม.*เกินกำหนด 2 วัน/)).toBeTruthy()
  // (4) ไม่มีทางอนุมัติแบบปกติ แต่มีทางปลดล็อก (override)
  expect(screen.queryByRole('button', { name: 'อนุมัติการยืม' })).toBeNull()
  expect(screen.getByRole('button', { name: /override/ })).toBeTruthy()
  // ((1)(2) สถานะคำขอและข้อมูลจาก API ตรวจด้วย pytest)
})
