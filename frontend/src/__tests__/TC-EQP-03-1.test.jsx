import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'

import EquipmentLoanPage from '../pages/EquipmentLoanPage.jsx'

// test จาก specs/007-equipment/test-cases.md ห้ามแก้ให้ผ่าน
const STUDENTS = [{ student_id: '64000001', name: 'นักศึกษาทดสอบ' }]

function studentClient(items, createLoanRequest = vi.fn().mockResolvedValue({ request_id: 'REQ-0001', status: 'pending', quantity: 1 })) {
  return {
    listEquipmentTypes: vi.fn().mockResolvedValue({ items }),
    listStudents: vi.fn().mockResolvedValue({ items: STUDENTS }),
    createLoanRequest,
  }
}

async function renderStudentPage(client, firstName) {
  render(<EquipmentLoanPage client={client} />)
  if (firstName) await screen.findByText(firstName)
  await screen.findByRole('option', { name: /นักศึกษาทดสอบ/ })
}

const THREE_TYPES = [
  { equipment_type_id: 'EQ-PLUG', name: 'ปลั๊กไฟ', available_count: 4 },
  { equipment_type_id: 'EQ-UMBRELLA', name: 'ร่ม', available_count: 2 },
  { equipment_type_id: 'EQ-BAG', name: 'ถุงผ้า', available_count: 5 },
]

test('test_TC_EQP_03_1_out_of_stock_not_allowed', async () => {
  // Given ถุงผ้าคงเหลือ 0 และนักศึกษาไม่มีรายการค้างคืน
  const items = THREE_TYPES.map((item) => (item.name === 'ถุงผ้า' ? { ...item, available_count: 0 } : item))
  const client = studentClient(items)
  await renderStudentPage(client, 'ถุงผ้า')

  // When นักศึกษาขอยืมถุงผ้า 1 ชิ้น
  fireEvent.click(screen.getByRole('button', { name: /ถุงผ้า/ }))
  const submit = screen.getByRole('button', { name: 'ส่งคำขอยืม' })
  fireEvent.click(submit)

  // Then (3) หน้าจอแสดง "ไม่สามารถยืมได้" และส่งคำขอยืมถุงผ้าไม่ได้
  // ((1)(2) คำตอบของ API และการไม่สร้างคำขอ ตรวจด้วย pytest)
  expect(screen.getByText('ไม่สามารถยืมได้')).toBeTruthy()
  expect(submit.disabled).toBe(true)
  expect(client.createLoanRequest).not.toHaveBeenCalled()
})
