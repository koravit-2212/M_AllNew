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

test('test_TC_EQP_01_3_no_equipment_in_system', async () => {
  // Given ระบบไม่มีรายการอุปกรณ์ให้บริการเลย
  const client = studentClient([])

  // When นักศึกษาเข้าหน้าจอยืมอุปกรณ์
  await renderStudentPage(client)
  await waitFor(() => expect(client.listEquipmentTypes).toHaveBeenCalled())

  // Then (1) API คืนรายการว่าง -> ไม่มีอุปกรณ์ให้เลือก
  expect(screen.queryAllByText(/คงเหลือ/)).toHaveLength(0)
  // (2) หน้าจอแสดงรายการว่าง และนักศึกษาส่งคำขอยืมไม่ได้ (Q-07)
  const submit = screen.getByRole('button', { name: 'ส่งคำขอยืม' })
  expect(submit.disabled).toBe(true)
  fireEvent.click(submit)
  expect(client.createLoanRequest).not.toHaveBeenCalled()
})
