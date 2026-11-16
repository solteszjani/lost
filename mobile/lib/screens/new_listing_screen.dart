import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';

class NewListingScreen extends StatefulWidget {
  const NewListingScreen({super.key});
  @override
  State<NewListingScreen> createState() => _NewListingScreenState();
}

class _NewListingScreenState extends State<NewListingScreen> {
  final form = GlobalKey<FormState>();
  final title = TextEditingController(), description = TextEditingController(), location = TextEditingController(), date = TextEditingController(), contact = TextEditingController();
  String kind = 'Elveszett', category = 'Egyéb';
  String? imagePath;
  bool busy = false;

  @override
  void dispose() { title.dispose(); description.dispose(); location.dispose(); date.dispose(); contact.dispose(); super.dispose(); }

  Future<void> _pickImage() async {
    final file = await ImagePicker().pickImage(source: ImageSource.gallery, imageQuality: 82, maxWidth: 1600);
    if (file != null) setState(() => imagePath = file.path);
  }

  Future<void> _submit() async {
    if (!form.currentState!.validate()) return;
    setState(() => busy = true);
    try {
      await ApiService.createListing({
        'kind': kind, 'title': title.text.trim(), 'description': description.text.trim(),
        'category': category, 'location': location.text.trim(), 'date': date.text.trim(),
        'contact': contact.text.trim(),
      }, imagePath: imagePath);
      if (mounted) Navigator.pop(context, true);
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
    } finally { if (mounted) setState(() => busy = false); }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Új bejelentés')),
    body: Form(key: form, child: ListView(padding: const EdgeInsets.all(16), children: [
      SegmentedButton<String>(segments: const [ButtonSegment(value: 'Elveszett', label: Text('Elveszett'), icon: Icon(Icons.search)), ButtonSegment(value: 'Talált', label: Text('Talált'), icon: Icon(Icons.volunteer_activism))], selected: {kind}, onSelectionChanged: (v) => setState(() => kind = v.first)),
      const SizedBox(height: 14),
      DropdownButtonFormField<String>(value: category, decoration: const InputDecoration(labelText: 'Kategória'), items: ['Kulcs','Telefon','Pénztárca','Iratok','Táska','Ékszer','Állat','Ruházat','Egyéb'].map((e) => DropdownMenuItem(value: e, child: Text(e))).toList(), onChanged: (v) { if (v != null) setState(() => category = v); }),
      const SizedBox(height: 12),
      TextFormField(controller: title, decoration: const InputDecoration(labelText: 'Megnevezés'), validator: (v) => (v == null || v.trim().length < 3) ? 'Adj meg legalább 3 karaktert.' : null),
      const SizedBox(height: 12),
      TextFormField(controller: description, maxLines: 4, decoration: const InputDecoration(labelText: 'Leírás'), validator: (v) => (v == null || v.trim().length < 10) ? 'A leírás legyen legalább 10 karakter.' : null),
      const SizedBox(height: 12),
      TextFormField(controller: location, decoration: const InputDecoration(labelText: 'Helyszín (ne adj meg pontos lakcímet)'), validator: (v) => (v == null || v.trim().isEmpty) ? 'A helyszín kötelező.' : null),
      const SizedBox(height: 12),
      TextFormField(controller: date, decoration: const InputDecoration(labelText: 'Dátum (pl. 2026-11-16)'), validator: (v) => (v == null || v.trim().isEmpty) ? 'A dátum kötelező.' : null),
      const SizedBox(height: 12),
      TextFormField(controller: contact, decoration: const InputDecoration(labelText: 'Kapcsolat (e-mail vagy telefonszám)'), validator: (v) => (v == null || v.trim().isEmpty) ? 'Adj meg elérhetőséget.' : null),
      const SizedBox(height: 14),
      OutlinedButton.icon(onPressed: _pickImage, icon: const Icon(Icons.photo_camera_back), label: Text(imagePath == null ? 'Fénykép hozzáadása' : 'Fénykép kiválasztva')),
      const SizedBox(height: 20),
      FilledButton(onPressed: busy ? null : _submit, child: Text(busy ? 'Mentés...' : 'Bejelentés közzététele')),
      const SizedBox(height: 8),
      const Text('Ne tölts fel személyes okmányt, bankkártyaadatot vagy más személy érzékeny adatát.', style: TextStyle(color: Colors.black54, fontSize: 12)),
    ])),
  );
}
