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

test('test_TC_EQP_03_3_in_stock_no_message', async () => {
  // Given ปลั๊กไฟคงเหลือ 4 ซึ่งไม่หมด
  const client = studentClient(THREE_TYPES)
  await renderStudentPage(client, 'ปลั๊กไฟ')

  // When นักศึกษาเลือกปลั๊กไฟ แล้วส่งคำขอยืม
  fireEvent.click(screen.getByRole('button', { name: /ปลั๊กไฟ/ }))
  // Then (1) หน้าจอไม่แสดงข้อความ "ไม่สามารถยืมได้"
  expect(screen.queryByText('ไม่สามารถยืมได้')).toBeNull()
  fireEvent.click(screen.getByRole('button', { name: 'ส่งคำขอยืม' }))

  // (2) ส่งคำขอได้ และได้คำขอสถานะรออนุมัติ
  await waitFor(() => expect(client.createLoanRequest).toHaveBeenCalledWith({ studentId: '64000001', equipmentTypeId: 'EQ-PLUG', quantity: 1 }))
  expect(await screen.findByText('ส่งคำขอแล้ว')).toBeTruthy()
})
