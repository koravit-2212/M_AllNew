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

test('test_TC_EQP_01_1_show_all_types_selectable', async () => {
  // Given ระบบมีอุปกรณ์ 3 ประเภท คือ ปลั๊กไฟ ร่ม ถุงผ้า และทุกประเภทมีคงเหลือมากกว่า 0
  const client = studentClient(THREE_TYPES)

  // When นักศึกษาเข้าหน้าจอยืมอุปกรณ์
  await renderStudentPage(client, 'ปลั๊กไฟ')

  // Then (1) เรียก API รายการประเภทอุปกรณ์
  expect(client.listEquipmentTypes).toHaveBeenCalled()
  // (2) หน้าจอแสดงชื่อทั้ง 3 ประเภทพร้อมจำนวนคงเหลือ
  for (const item of THREE_TYPES) {
    expect(screen.getByText(item.name)).toBeTruthy()
    expect(screen.getByText(`คงเหลือ ${item.available_count}`)).toBeTruthy()
  }
  // (3) นักศึกษากดเลือกประเภทใดประเภทหนึ่งได้
  const umbrella = screen.getByRole('button', { name: /ร่ม/ })
  fireEvent.click(umbrella)
  expect(umbrella.getAttribute('aria-pressed')).toBe('true')
})
