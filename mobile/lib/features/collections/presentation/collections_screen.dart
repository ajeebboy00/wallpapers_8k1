import 'package:flutter/material.dart';

class CollectionsScreen extends StatelessWidget {
  const CollectionsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Collections', style: TextStyle(fontWeight: FontWeight.bold)),
      ),
      body: const Center(
        child: Text('Curated Collections', style: TextStyle(color: Colors.grey)),
      ),
    );
  }
}
