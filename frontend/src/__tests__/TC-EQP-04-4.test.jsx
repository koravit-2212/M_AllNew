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

test('test_TC_EQP_04_4_no_outstanding_normal_approve', async () => {
  // Given นักศึกษาไม่มีรายการค้างคืน และปลั๊กไฟคงเหลือ 4
  const client = staffClient(pending(), LOAN_RESULT)

  // When นักศึกษาขอยืมปลั๊กไฟ แล้วเจ้าหน้าที่เปิดคำขอ
  await openRequest(client)

  // Then (2) หน้าจอไม่แสดงคำเตือนรายการค้างคืน และแสดงว่าไม่มีรายการค้างคืน
  expect(screen.queryByText('มีรายการค้างคืน')).toBeNull()
  expect(within(screen.getByLabelText('ข้อมูลคำขอ')).getByText('ไม่มี')).toBeTruthy()
  // (3) มีปุ่มอนุมัติแบบปกติ และไม่มีปุ่ม override
  expect(screen.getByRole('button', { name: 'อนุมัติการยืม' })).toBeTruthy()
  expect(screen.queryByRole('button', { name: /override/ })).toBeNull()
  // ((1) ข้อมูลจาก API ตรวจด้วย pytest)
})
