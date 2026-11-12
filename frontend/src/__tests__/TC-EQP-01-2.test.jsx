import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
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

test('test_TC_EQP_01_2_zero_stock_type_in_list', async () => {
  // Given ประเภทหนึ่งมีคงเหลือ 0 อีก 2 ประเภทคงเหลือ 1 ขึ้นไป
  const items = THREE_TYPES.map((item) => (item.name === 'ถุงผ้า' ? { ...item, available_count: 0 } : item))
  const client = studentClient(items)

  // When นักศึกษาเข้าหน้าจอยืมอุปกรณ์
  await renderStudentPage(client, 'ถุงผ้า')

  // Then (1) ประเภทที่คงเหลือ 1 ขึ้นไปแสดงให้เลือกได้
  expect(screen.getByRole('button', { name: /ปลั๊กไฟ/ })).toBeTruthy()
  expect(screen.getByRole('button', { name: /ร่ม/ })).toBeTruthy()
  // (2) ประเภทที่คงเหลือ 0 แสดงในรายการ พร้อมระบุว่าหมด (Q-06)
  const bag = screen.getByRole('button', { name: /ถุงผ้า/ })
  expect(within(bag).getByText('คงเหลือ 0')).toBeTruthy()
  expect(within(bag).getByText(/หมด/)).toBeTruthy()
  // (3) เลือกประเภทที่คงเหลือ 0 แล้วแจ้งว่า "ไม่สามารถยืมได้"
  fireEvent.click(bag)
  expect(screen.getByText('ไม่สามารถยืมได้')).toBeTruthy()
})
